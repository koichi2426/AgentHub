import os
import paramiko
import stat
from typing import Optional, Dict, BinaryIO # Dict, BinaryIO を追加
# Import Protocol if needed for type hinting the interface
from domain.services.file_storage_domain_service import FileStorageDomainService 

# Define UploadedFileStream locally if not importable or adjust path
try:
    from domain.value_objects.file_data import UploadedFileStream
except ImportError:
    # Define locally if necessary
    class UploadedFileStream: # Dummy protocol implementation
        @property
        def filename(self) -> str: ...
        @property
        def file_stream(self) -> BinaryIO: ...

# Define FileStorageError locally if not importable
try:
    # Attempt to import if it exists elsewhere, e.g., in a shared infrastructure module
    from infrastructure.storage.local_file_storage import FileStorageError
except ImportError:
    class FileStorageError(Exception):
        """ファイルストレージ操作に関するカスタムエラー"""
        pass


class SFTPFileStorageDomainServiceImpl(FileStorageDomainService):
    """
    FileStorageDomainService の本番実装。
    Paramiko (SFTP) を使用して、リモートVPSとのファイル操作を行う。
    """
    def __init__(self, vps_ip: str, vps_user: str, vps_account_password: str,
                 key_file_path: str, remote_training_dir: str,
                 remote_model_dir: str, vps_port: int = 22):

        self.vps_ip = vps_ip
        self.vps_user = vps_user
        self.vps_account_password = vps_account_password
        self.vps_port = vps_port
        self.key_file_path = key_file_path
        # Store base directories consistently
        self.remote_training_base_dir = remote_training_dir
        self.remote_model_base_dir = remote_model_dir
        # Define visualization base dir (could be env var or derived)
        self.remote_visuals_base_dir = f"/home/{self.vps_user}/visualizations"

        if not os.path.exists(self.key_file_path):
            raise FileNotFoundError(f"SSH key file not found at: {self.key_file_path}")

        try:
            # Load private key once during initialization
            self.private_key = paramiko.RSAKey(filename=self.key_file_path)
        except Exception as e:
            raise FileStorageError(f"Failed to load SSH private key: {e}")

        print(f"INFO: SFTP Storage Service initialized. Target: {self.vps_user}@{self.vps_ip} (with 2FA)")
        print(f"INFO: -> Training Base Dir: {self.remote_training_base_dir}")
        print(f"INFO: -> Model Base Dir: {self.remote_model_base_dir}")
        print(f"INFO: -> Visuals Base Dir: {self.remote_visuals_base_dir}") # Log visuals dir

    def _connect_sftp(self) -> paramiko.SFTPClient:
        """Establishes SFTP connection and returns the client."""
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print(f"INFO: Connecting to {self.vps_ip} via SFTP...")
            client.connect(
                self.vps_ip,
                port=self.vps_port,
                username=self.vps_user,
                password=self.vps_account_password,
                pkey=self.private_key
            )
            sftp = client.open_sftp()
            print(f"INFO: SFTP connection established.")
            # Store the underlying transport to close it properly later
            sftp._transport = client._transport # type: ignore
            return sftp
        except Exception as e:
            print(f"ERROR: Failed to connect SFTP: {e}")
            if client:
                client.close() # Ensure client is closed on connection error
            raise FileStorageError(f"Failed to connect SFTP: {e}")

    def _close_sftp(self, sftp: Optional[paramiko.SFTPClient]):
        """Closes the SFTP session and the underlying SSH connection."""
        if not sftp:
            return
        try:
            sftp.close()
            # Close the transport associated with the SFTP client
            if hasattr(sftp, '_transport') and sftp._transport: # type: ignore
                 transport = sftp._transport # type: ignore
                 if transport.is_active():
                     transport.close()
            print("INFO: SFTP Connection closed.")
        except Exception as e:
            print(f"WARN: Error closing SFTP connection: {e}")

    def _ensure_remote_dir(self, sftp: paramiko.SFTPClient, remote_dir: str):
        """Ensures the remote directory exists, creating it recursively if necessary."""
        current_dir = ""
        # Handle absolute paths starting with /
        if not remote_dir.startswith('/'):
            raise ValueError("Remote directory path must be absolute (start with '/')")
            
        parts = remote_dir.strip('/').split('/')
        if remote_dir.startswith('/'):
             parts.insert(0,'') # Keep the leading slash logic

        for part in parts:
            # Skip empty parts resulting from multiple slashes or leading slash handled above
            if not part and current_dir != "": 
                continue
            
            # For root directory, current_dir is just '/'
            if current_dir == "":
                current_dir = "/" if part == "" else "/" + part
            elif current_dir == "/":
                 current_dir += part
            else:
                current_dir += "/" + part
                
            # Skip checking/creating root
            if current_dir == "/":
                 continue

            try:
                sftp_attrs = sftp.stat(current_dir)
                if not stat.S_ISDIR(sftp_attrs.st_mode):
                    raise FileStorageError(f"Remote path {current_dir} exists but is not a directory.")
            except FileNotFoundError:
                print(f"INFO: Creating remote directory: {current_dir}")
                try:
                    sftp.mkdir(current_dir)
                except Exception as mkdir_e:
                     # Handle potential race conditions or permission issues
                     try: # Check again if it was created by another process
                          sftp.stat(current_dir) 
                     except FileNotFoundError:
                          raise FileStorageError(f"Failed to create remote directory {current_dir}: {mkdir_e}")
            except Exception as e:
                 raise FileStorageError(f"Error checking/creating remote directory {current_dir}: {e}")
        print(f"INFO: Remote directory structure {remote_dir} ensured.")


    # --- Interface Methods Implementation ---

    def save_training_file(self, uploaded_file: UploadedFileStream, unique_id: str) -> str:
        """訓練データファイルを保存する。"""
        filename = f"{unique_id}_{uploaded_file.filename}"
        remote_path = os.path.join(self.remote_training_base_dir, filename).replace("\\", "/")
        sftp = None
        try:
            sftp = self._connect_sftp()
            self._ensure_remote_dir(sftp, self.remote_training_base_dir)
            
            actual_binary_stream = uploaded_file.file_stream
            actual_binary_stream.seek(0)
            
            print(f"INFO: Uploading training file to SFTP: {remote_path}...")
            sftp.putfo(actual_binary_stream, remote_path)
            print(f"INFO: Upload successful.")
            
            return remote_path
        except Exception as e:
            print(f"ERROR: Failed to save training file via SFTP. Error: {e}")
            raise FileStorageError(f"Failed to save training file to VPS: {e}")
        finally:
            self._close_sftp(sftp)

    # save_training_model might be deprecated by upload_directory, but implement if needed
    def save_training_model(self, model_artifact: UploadedFileStream, unique_id: str) -> str:
        """単一の訓練モデルファイルを保存する (job ID フォルダ内に)。"""
        # Assume unique_id is job_id for models
        job_id = unique_id
        remote_job_model_dir = os.path.join(self.remote_model_base_dir, f"job_{job_id}").replace("\\", "/")
        filename = model_artifact.filename # Use original artifact name
        remote_path = os.path.join(remote_job_model_dir, filename).replace("\\", "/")
        sftp = None
        try:
            sftp = self._connect_sftp()
            self._ensure_remote_dir(sftp, remote_job_model_dir)

            actual_binary_stream = model_artifact.file_stream
            actual_binary_stream.seek(0)

            print(f"INFO: Uploading model artifact to SFTP: {remote_path}...")
            sftp.putfo(actual_binary_stream, remote_path)
            print(f"INFO: Upload successful.")

            return remote_path
        except Exception as e:
            print(f"ERROR: Failed to save model artifact via SFTP. Error: {e}")
            raise FileStorageError(f"Failed to save model artifact to VPS: {e}")
        finally:
            self._close_sftp(sftp)


    def download_file(self, remote_path: str, local_path: str) -> None:
        """リモートファイルをローカルにダウンロードする。"""
        sftp = None
        try:
            sftp = self._connect_sftp()
            # ローカルディレクトリが存在しない場合は作成
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                print(f"INFO: Creating local directory: {local_dir}")
                os.makedirs(local_dir, exist_ok=True)
                
            print(f"INFO: Downloading {remote_path} to {local_path}...")
            sftp.get(remote_path, local_path)
            print(f"INFO: Download successful.")
        except Exception as e:
            print(f"ERROR: Failed to download file via SFTP. Error: {e}")
            raise FileStorageError(f"Failed to download file {remote_path}: {e}")
        finally:
            self._close_sftp(sftp)

    def upload_directory(self, local_dir_path: str, remote_base_dir: str,
                         return_remote_paths: bool = False) -> Dict[str, str]:
        """ローカルディレクトリの内容をリモートにアップロードする。"""
        sftp = None
        uploaded_paths: Dict[str, str] = {}
        try:
            sftp = self._connect_sftp()
            # Ensure base remote directory exists first
            self._ensure_remote_dir(sftp, remote_base_dir)

            print(f"INFO: Uploading directory contents from {local_dir_path} to {remote_base_dir}...")
            
            # Walk through the local directory
            for root, dirs, files in os.walk(local_dir_path):
                # Calculate relative path from the base local directory
                relative_path = os.path.relpath(root, local_dir_path)
                
                # Determine remote directory path
                if relative_path == ".":
                    remote_current_dir = remote_base_dir
                else:
                    # Construct remote path ensuring forward slashes
                    remote_current_dir = os.path.join(remote_base_dir, relative_path).replace("\\", "/")
                    # Ensure subdirectory exists remotely
                    self._ensure_remote_dir(sftp, remote_current_dir)

                # Upload files in the current directory
                for filename in files:
                    local_file = os.path.join(root, filename)
                    # Construct remote file path ensuring forward slashes
                    remote_file = os.path.join(remote_current_dir, filename).replace("\\", "/")
                    
                    print(f"INFO:   Uploading {local_file} -> {remote_file}")
                    sftp.put(local_file, remote_file)
                    
                    if return_remote_paths:
                        # Store mapping using relative local path as key
                        local_relative = os.path.relpath(local_file, local_dir_path).replace("\\", "/")
                        uploaded_paths[local_relative] = remote_file

            print(f"INFO: Directory upload successful.")
            return uploaded_paths

        except Exception as e:
            print(f"ERROR: Failed to upload directory via SFTP. Error: {e}")
            raise FileStorageError(f"Failed to upload directory {local_dir_path}: {e}")
        finally:
            self._close_sftp(sftp)

# --- Factory Function (No changes needed if it uses env vars correctly) ---
def NewFileStorageDomainService() -> FileStorageDomainService:
    """
    FileStorageDomainService のファクトリ関数。
    環境変数を読み込み、SFTPサービスを初期化する。
    """
    print("INFO: Initializing SFTPFileStorageDomainServiceImpl from environment variables...")
    try:
        vps_ip = os.environ["VPS_IP"]
        vps_user = os.environ["VPS_USER"]
        vps_account_password = os.environ["VPS_ACCOUNT_PASSWORD"]
        key_file_path = os.environ["VPS_KEY_FILE_PATH"]
        vps_port = int(os.environ.get("VPS_PORT", 22))

        remote_training_dir = os.environ.get("VPS_TRAINING_DIR", f"/home/{vps_user}/training_data")
        remote_model_dir = os.environ.get("VPS_MODEL_DIR", f"/home/{vps_user}/models")

        return SFTPFileStorageDomainServiceImpl(
            vps_ip=vps_ip,
            vps_user=vps_user,
            vps_account_password=vps_account_password,
            key_file_path=key_file_path,
            remote_training_dir=remote_training_dir, # Pass base dir
            remote_model_dir=remote_model_dir,       # Pass base dir
            vps_port=vps_port
        )
    except KeyError as e:
        msg = f"FATAL: Missing environment variable for SFTP setup: {e}."
        print(msg)
        raise EnvironmentError(msg)
    except Exception as e:
        msg = f"FATAL: Failed to initialize SFTPFileStorageDomainService: {e}"
        print(msg)
        raise