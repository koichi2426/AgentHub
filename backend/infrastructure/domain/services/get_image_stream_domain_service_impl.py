import os
import mimetypes
from io import BytesIO
from typing import Tuple, Optional, BinaryIO
import paramiko # SFTP接続用

# 抽象ドメインオブジェクト/サービスのインポート
# ★★★ 修正: パスを変更 ★★★
from domain.services.get_image_stream_domain_service import FileStreamDomainService 
from domain.value_objects.binary_stream import BinaryStream 

# 既存のSFTP実装に必要な依存関係 (エラー処理)
class FileStreamError(Exception):
    """ファイルストリーム操作に関するカスタムエラー"""
    pass


class SFTPFileStreamDomainServiceImpl(FileStreamDomainService):
    """
    FileStreamDomainService の具体的な実装。
    SFTP接続を利用して、リモートVPSからファイルをBinaryStreamとして取得する。
    """
    def __init__(self, vps_ip: str, vps_user: str, vps_password: str, vps_key_path: str, vps_port: int, remote_visuals_base_dir: str):
        self._vps_ip = vps_ip
        self._vps_user = vps_user
        self._vps_password = vps_password
        self._vps_key_path = vps_key_path
        self._vps_port = vps_port
        self._remote_visuals_base_dir = remote_visuals_base_dir
        
        # 鍵のロード
        if not os.path.exists(self._vps_key_path):
             raise FileNotFoundError(f"SSH key not found: {self._vps_key_path}")
        try:
             self._private_key = paramiko.RSAKey(filename=self._vps_key_path)
        except Exception as e:
             raise FileStreamError(f"Failed to load SSH key: {e}")

    # --- SFTP接続ヘルパー ---
    def _connect_sftp(self) -> paramiko.SFTPClient:
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                self._vps_ip, port=self._vps_port, username=self._vps_user,
                password=self._vps_password, pkey=self._private_key
            )
            return client.open_sftp()
        except Exception as e:
            if client: client.close()
            raise FileStreamError(f"SFTP connection failed: {e}")

    def _close_sftp(self, sftp: paramiko.SFTPClient):
        # SSHクライアントも閉じる
        if sftp:
            try:
                sftp.close()
                if hasattr(sftp, '_transport') and sftp._transport: # type: ignore
                     sftp._transport.close() # type: ignore
            except Exception: pass


    # --- FileStreamDomainService インターフェース実装 ---

    def get_file_stream_by_path(self, relative_path: str) -> Tuple[BinaryStream, str]:
        """
        相対パスからVPS上の画像をストリームとして取得し、BinaryStreamとMIMEタイプを返す。
        """
        # 1. VPS上の絶対パスを構築
        # relative_path は 'job_ID/layer0/image.png' 形式
        vps_absolute_path = os.path.join(self._remote_visuals_base_dir, relative_path).replace("\\", "/")
        
        sftp = None
        
        try:
            # 2. SFTP接続
            sftp = self._connect_sftp()
            
            # 3. ファイルをBytesIOストリームにダウンロード
            # BytesIOはBinaryStreamプロトコルを満たす
            mem_stream = BytesIO() 
            sftp.getfo(vps_absolute_path, mem_stream)
            
            mem_stream.seek(0) # ポインタを先頭に戻す
            
            # 4. MIMEタイプを判定
            mime_type, _ = mimetypes.guess_type(vps_absolute_path)
            mime_type = mime_type if mime_type and mime_type.startswith('image/') else 'application/octet-stream'

            # 5. 結果を抽象型で返す (BytesIOはプロトコルを満たす)
            return mem_stream, mime_type
            
        except FileNotFoundError as e:
             raise FileStreamError(f"Image not found on VPS: {vps_absolute_path}")
        except Exception as e:
             raise FileStreamError(f"Error streaming file from VPS: {e}")
        finally:
             if sftp: self._close_sftp(sftp)


# === ファクトリ関数 ===
def NewFileStreamDomainService() -> FileStreamDomainService:
    """環境変数から設定を読み込み、SFTPFileStreamDomainServiceImplを初期化する。"""
    try:
        # 環境変数はrouter/fastapi.pyで既に読み込まれている前提
        vps_ip = os.environ["VPS_IP"]
        vps_user = os.environ["VPS_USER"]
        vps_password = os.environ["VPS_ACCOUNT_PASSWORD"]
        vps_key_path = os.environ["VPS_KEY_FILE_PATH"]
        vps_port = int(os.environ.get("VPS_PORT", 22))
        
        # VPS_VISUALS_DIR が .env に設定されていることを前提とする
        vps_visuals_dir = os.environ.get("VPS_VISUALS_DIR", f"/home/{vps_user}/visualizations")

        return SFTPFileStreamDomainServiceImpl(
            vps_ip=vps_ip, vps_user=vps_user, vps_password=vps_password, 
            vps_key_path=vps_key_path, vps_port=vps_port,
            remote_visuals_base_dir=vps_visuals_dir
        )
    except Exception as e:
        print(f"FATAL: Failed to initialize FileStreamDomainService: {e}")
        raise EnvironmentError(f"Failed to initialize FileStreamDomainService: {e}")