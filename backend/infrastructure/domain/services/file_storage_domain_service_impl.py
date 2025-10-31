import os
import paramiko
import stat
from typing import Optional
from domain.services.file_storage_domain_service import FileStorageDomainService
from domain.value_objects.file_data import UploadedFileStream
from infrastructure.storage.local_file_storage import save_training_file, FileStorageError
# --- 必要な鍵クラスをインポート ---
from paramiko.ed25519key import Ed25519Key



class SFTPFileStorageDomainServiceImpl(FileStorageDomainService):
    """
    FileStorageDomainService の本番実装。
    Paramiko (SFTP) を使用して、リモートVPSにファイルを保存する。
    """
    
    # --- パスワード引数を __init__ から削除 ---
    def __init__(self, vps_ip: str, vps_user: str,
                 key_file_path: str, remote_training_dir: str, 
                 remote_model_dir: str, vps_port: int = 22):
        
        self.vps_ip = vps_ip
        self.vps_user = vps_user
        self.vps_port = vps_port
        self.key_file_path = key_file_path
        self.remote_training_dir = remote_training_dir
        self.remote_model_dir = remote_model_dir
        
        if not os.path.exists(self.key_file_path):
            raise FileNotFoundError(f"SSH key file not found at: {self.key_file_path}")
        
        # --- RSAKey を Ed25519Key に変更 ---
        try:
            self.private_key = paramiko.Ed25519Key(filename=self.key_file_path)
        except Exception as e:
            raise FileStorageError(f"Failed to load SSH private key (tried Ed25519): {e}")

        print(f"INFO: SFTP Storage Service initialized. Target: {vps_user}@{vps_ip}") 
        print(f"INFO: -> Training Dir: {self.remote_training_dir}")
        print(f"INFO: -> Model Dir: {self.remote_model_dir}")

    # --- ▼▼▼ 修正点 8: 堅牢な「再帰的mkdir」ヘルパーを追加 ▼▼▼ ---
    def _ensure_remote_dir_recursive(self, sftp: paramiko.SFTPClient, remote_dir: str):
        """
        リモートディレクトリが存在することを確認し、なければ再帰的に作成する。
        Windowsの /C/Users/... パスにも対応。
        """
        current_dir = ""
        # remote_dir を / で分割 (例: /C/Users/satoy/training_data)
        parts = remote_dir.split('/') 
        
        for part in parts:
            if not part: # 最初の '/' は無視
                current_dir = "/"
                continue
            
            # パスを構築 (例: /C, /C/Users, /C/Users/satoy, ...)
            if current_dir == "/":
                current_dir += part
            else:
                current_dir += "/" + part
            
            try:
                sftp_attrs = sftp.stat(current_dir)
                if not stat.S_ISDIR(sftp_attrs.st_mode):
                    raise FileStorageError(f"Path exists but is not directory: {current_dir}")
            except FileNotFoundError:
                # 見つからなかったら、作る
                print(f"INFO: Creating remote directory: {current_dir}")
                try:
                    sftp.mkdir(current_dir)
                except Exception as mkdir_e:
                     # 競合状態 (race condition) や権限エラーなどをハンドル
                     raise FileStorageError(f"Failed to create remote dir {current_dir}: {mkdir_e}")
            except Exception as e:
                 raise FileStorageError(f"Error checking dir {current_dir}: {e}")
    # --- ▲▲▲ 修正点 8 完了 ▲▲▲ ---

    def _save_file(self, file_stream: UploadedFileStream, remote_dir: str, filename: str) -> str:
        """SFTPでファイルをアップロードする共通ヘルパー"""
        
        remote_path = f"{remote_dir}/{filename}"
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            print(f"INFO: Connecting to {self.vps_ip} via SFTP...")
            
            # --- connect() から password 引数を削除 ---
            client.connect(
                self.vps_ip, 
                port=self.vps_port, 
                username=self.vps_user,
                pkey=self.private_key
            )

            sftp = client.open_sftp()
            
            # --- ▼▼▼ 修正点 9: 脆弱なmkdirを、堅牢な再帰的mkdirの呼び出しに置き換え ▼▼▼ ---
            # リモートディレクトリの存在確認と自動作成
            try:
                self._ensure_remote_dir_recursive(sftp, remote_dir)
            except Exception as dir_e:
                raise FileStorageError(f"Failed to ensure remote directory {remote_dir}: {dir_e}")
            # --- ▲▲▲ 修正点 9 完了 ▲▲▲ ---

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
        
        # --- 不要なパスワード読み込みを削除 ---
        # vps_account_password = os.environ["VPS_ACCOUNT_PASSWORD"]
        
        key_file_path = os.environ["VPS_KEY_FILE_PATH"] # .env で /run/secrets/vps_key_ed25519 などを指定
        vps_port = int(os.environ.get("VPS_PORT", 22)) # .env で 1720 などを指定
        
        # --- 接続先はWindows (satoy機) なので、デフォルトパスをWindows形式に変更 ---
        remote_training_dir = os.environ.get("VPS_TRAINING_DIR", f"/C/Users/{vps_user}/training_data")
        remote_model_dir = os.environ.get("VPS_MODEL_DIR", f"/C/Users/{vps_user}/models")


        # --- インスタンス化からパスワード引数を削除 ---
        return SFTPFileStorageDomainServiceImpl(
            vps_ip=vps_ip,
            vps_user=vps_user,
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
