import os
import paramiko
import stat
from typing import Optional
from domain.services.file_storage_domain_service import FileStorageDomainService
from domain.value_objects.file_data import UploadedFileStream
from local_file_storage import save_training_file, FileStorageError


class SFTPFileStorageDomainServiceImpl(FileStorageDomainService):
    """
    FileStorageDomainService の本番実装。
    Paramiko (SFTP) を使用して、リモートVPSにファイルを保存する。
    """
    def __init__(self, vps_ip: str, vps_user: str, vps_account_password: str,
                 key_file_path: str, remote_training_dir: str, 
                 remote_model_dir: str, vps_port: int = 22):
        
        self.vps_ip = vps_ip
        self.vps_user = vps_user
        self.vps_account_password = vps_account_password
        self.vps_port = vps_port
        self.key_file_path = key_file_path
        self.remote_training_dir = remote_training_dir
        self.remote_model_dir = remote_model_dir
        
        if not os.path.exists(self.key_file_path):
            raise FileNotFoundError(f"SSH key file not found at: {self.key_file_path}")
        
        try:
            self.private_key = paramiko.RSAKey(filename=self.key_file_path)
        except Exception as e:
            raise FileStorageError(f"Failed to load SSH private key: {e}")

        print(f"INFO: SFTP Storage Service initialized. Target: {vps_user}@{vps_ip} (with 2FA)")
        print(f"INFO: -> Training Dir: {self.remote_training_dir}")
        print(f"INFO: -> Model Dir: {self.remote_model_dir}")

    def _save_file(self, file_stream: UploadedFileStream, remote_dir: str, filename: str) -> str:
        """SFTPでファイルをアップロードする共通ヘルパー"""
        
        remote_path = f"{remote_dir}/{filename}"
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
            
            # リモートディレクトリの存在確認と自動作成
            try:
                sftp_attrs = sftp.stat(remote_dir)
                if not stat.S_ISDIR(sftp_attrs.st_mode):
                    raise FileStorageError(f"Remote path {remote_dir} exists but is not a directory.")
            except FileNotFoundError:
                print(f"INFO: Remote directory {remote_dir} not found. Creating...")
                sftp.mkdir(remote_dir)
                print(f"INFO: Remote directory {remote_dir} created.")

            # ファイルをストリームで転送
            actual_binary_stream = file_stream.file_stream
            actual_binary_stream.seek(0)
            
            print(f"INFO: Uploading to SFTP: {remote_path}...")
            sftp.putfo(actual_binary_stream, remote_path)
            print(f"INFO: Upload successful.")
            
            sftp.close()
            
            return remote_path

        except Exception as e:
            print(f"ERROR: Failed to upload file via SFTP. Error: {e}")
            raise FileStorageError(f"Failed to save file to VPS: {e}")
        finally:
            if client:
                client.close()
                print("INFO: SFTP Connection closed.")

    def save_training_file(self, uploaded_file: UploadedFileStream, unique_id: str) -> str:
        """
        訓練データファイルを保存する。
        """
        filename = f"{unique_id}_{uploaded_file.filename}"
        return self._save_file(
            file_stream=uploaded_file,
            remote_dir=self.remote_training_dir,
            filename=filename
        )

    def save_training_model(self, model_artifact: UploadedFileStream, unique_id: str) -> str:
        """
        訓練モデルファイルを保存する。
        """
        filename = f"{unique_id}_{model_artifact.filename}"
        return self._save_file(
            file_stream=model_artifact,
            remote_dir=self.remote_model_dir,
            filename=filename
        )


def NewFileStorageDomainService() -> FileStorageDomainService:
    """
    FileStorageDomainService のファクトリ関数。
    環境変数を読み込み、SFTPサービスを初期化する。
    """
    print("INFO: Initializing SFTPFileStorageDomainServiceImpl")
    try:
        # 環境変数から本番用の設定を読み込む
        vps_ip = os.environ["VPS_IP"]
        vps_user = os.environ["VPS_USER"]
        vps_account_password = os.environ["VPS_ACCOUNT_PASSWORD"]
        key_file_path = os.environ["VPS_KEY_FILE_PATH"] 
        vps_port = int(os.environ.get("VPS_PORT", 22))
        
        remote_training_dir = os.environ.get("VPS_TRAINING_DIR", f"/home/{vps_user}/training_data")
        remote_model_dir = os.environ.get("VPS_MODEL_DIR", f"/home/{vps_user}/models")

        # 本番用の実装を初期化して返す
        return SFTPFileStorageDomainServiceImpl(
            vps_ip=vps_ip,
            vps_user=vps_user,
            vps_account_password=vps_account_password,
            key_file_path=key_file_path,
            remote_training_dir=remote_training_dir,
            remote_model_dir=remote_model_dir,
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

