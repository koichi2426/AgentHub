# worker/tasks/finetuning/sftp_service.py

import os
import paramiko
import stat
from typing import Optional, Dict, Any
from contextlib import contextmanager

# Define Error class locally
class FileStorageError(Exception):
    """ファイルストレージ操作に関するカスタムエラー"""
    pass

class SFTPFileStorageService:
    """Paramiko (SFTP) を使用して、リモートVPSとのファイル操作を行うサービス。"""
    def __init__(self, vps_ip: str, vps_user: str, vps_account_password: str,
                 key_file_path: str, remote_training_dir: str,
                 remote_model_dir: str, remote_visuals_dir: str,
                 vps_port: int = 22):

        self.vps_ip = vps_ip
        self.vps_user = vps_user
        self.vps_account_password = vps_account_password
        self.vps_port = vps_port
        self.key_file_path = key_file_path
        self.remote_training_base_dir = remote_training_dir
        self.remote_model_base_dir = remote_model_dir
        self.remote_visuals_base_dir = remote_visuals_dir

        if not os.path.exists(self.key_file_path):
            raise FileNotFoundError(f"SSH key file not found: {self.key_file_path}")
        try:
            self.private_key = paramiko.RSAKey(filename=self.key_file_path)
        except Exception as e:
            raise FileStorageError(f"Failed to load SSH private key: {e}")

        print(f"INFO: SFTP Storage Service initialized for {self.vps_user}@{self.vps_ip}")

    @contextmanager
    def connect(self) -> paramiko.SFTPClient:
        """SFTP接続を管理するコンテキストマネージャ"""
        client = None
        sftp = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # print(f"DEBUG: Connecting SFTP...") # Reduced logging
            client.connect(
                self.vps_ip, port=self.vps_port, username=self.vps_user,
                password=self.vps_account_password, pkey=self.private_key
            )
            sftp = client.open_sftp()
            # print(f"DEBUG: SFTP connected.") # Reduced logging
            yield sftp
        except Exception as e:
            print(f"ERROR: SFTP connection/operation failed: {e}")
            raise FileStorageError(f"SFTP operation failed: {e}")
        finally:
            if sftp:
                try: sftp.close()
                except Exception: pass # Ignore close errors
            if client:
                try: client.close()
                except Exception: pass # Ignore close errors
            # print("DEBUG: SFTP Connection closed.") # Reduced logging

    def _ensure_remote_dir_internal(self, sftp: paramiko.SFTPClient, remote_dir: str):
        """リモートディレクトリが存在することを確認し、なければ再帰的に作成"""
        current_dir = ""
        if not remote_dir.startswith('/'): raise ValueError("Remote path must be absolute")
        parts = remote_dir.strip('/').split('/')
        if remote_dir.startswith('/'): parts.insert(0,'')

        for part in parts:
            if not part and current_dir != "": continue
            current_dir = "/" if current_dir == "" and part == "" else (current_dir + "/" + part).replace('//','/')
            if current_dir == "/": continue # Skip root
            try:
                sftp_attrs = sftp.stat(current_dir)
                if not stat.S_ISDIR(sftp_attrs.st_mode):
                    raise FileStorageError(f"Path exists but is not directory: {current_dir}")
            except FileNotFoundError:
                # print(f"DEBUG: Creating remote directory: {current_dir}") # Reduced logging
                try:
                    sftp.mkdir(current_dir)
                except Exception as mkdir_e:
                     try: sftp.stat(current_dir); # Check again for race condition
                     except FileNotFoundError: raise FileStorageError(f"Failed create dir {current_dir}: {mkdir_e}")
            except Exception as e: raise FileStorageError(f"Error ensuring dir {current_dir}: {e}")

    def download_file(self, remote_path: str, local_path: str):
        """リモートファイルをローカルにダウンロード"""
        with self.connect() as sftp:
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir): os.makedirs(local_dir, exist_ok=True)
            print(f"INFO: Downloading {remote_path} to {local_path}...")
            sftp.get(remote_path, local_path)
            print(f"INFO: Download successful.")

    def upload_directory(self, local_dir_path: str, remote_base_dir: str,
                         return_remote_paths: bool = False) -> Dict[str, str]:
        """ローカルディレクトリの内容をリモートにアップロード"""
        uploaded_paths = {}
        with self.connect() as sftp:
            self._ensure_remote_dir_internal(sftp, remote_base_dir)
            print(f"INFO: Uploading dir {local_dir_path} to {remote_base_dir}...")
            for root, dirs, files in os.walk(local_dir_path):
                relative_path = os.path.relpath(root, local_dir_path)
                remote_current_dir = remote_base_dir if relative_path == "." else os.path.join(remote_base_dir, relative_path).replace("\\", "/")
                if relative_path != ".": self._ensure_remote_dir_internal(sftp, remote_current_dir)
                for filename in files:
                    local_file = os.path.join(root, filename)
                    remote_file = os.path.join(remote_current_dir, filename).replace("\\", "/")
                    # print(f"DEBUG:   Uploading {local_file} -> {remote_file}") # Reduced logging
                    sftp.put(local_file, remote_file)
                    if return_remote_paths:
                        local_relative = os.path.relpath(local_file, local_dir_path).replace("\\", "/")
                        uploaded_paths[local_relative] = remote_file
            print(f"INFO: Directory upload successful.")
        return uploaded_paths

def create_sftp_service_from_env() -> SFTPFileStorageService:
    """環境変数からSFTPサービスインスタンスを生成"""
    print("INFO: Initializing SFTPFileStorageService from env...")
    try:
        # 環境変数読み込み (必須項目がない場合は KeyError)
        vps_ip=os.environ["VPS_IP"]; vps_user=os.environ["VPS_USER"]
        vps_account_password=os.environ["VPS_ACCOUNT_PASSWORD"]
        key_file_path=os.environ["VPS_KEY_FILE_PATH"]
        vps_port=int(os.environ.get("VPS_PORT", 22))
        remote_training_dir=os.environ.get("VPS_TRAINING_DIR", f"/home/{vps_user}/training_data")
        remote_model_dir=os.environ.get("VPS_MODEL_DIR", f"/home/{vps_user}/models")
        remote_visuals_dir=os.environ.get("VPS_VISUALS_DIR", f"/home/{vps_user}/visualizations") # Visuals dir from env

        return SFTPFileStorageService(
            vps_ip=vps_ip, vps_user=vps_user, vps_account_password=vps_account_password,
            key_file_path=key_file_path, remote_training_dir=remote_training_dir,
            remote_model_dir=remote_model_dir, remote_visuals_dir=remote_visuals_dir,
            vps_port=vps_port
        )
    except KeyError as e: msg = f"FATAL: Missing env var for SFTP: {e}"; print(msg); raise EnvironmentError(msg)
    except Exception as e: msg = f"FATAL: Failed to init SFTPService: {e}"; print(msg); raise
