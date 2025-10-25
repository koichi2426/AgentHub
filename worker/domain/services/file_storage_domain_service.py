import abc
from typing import Protocol, Optional, Dict # Dict を追加

from domain.value_objects.file_data import UploadedFileStream

class FileStorageDomainService(Protocol):
    """
    ファイル（訓練データ、モデル成果物、可視化画像など）を
    永続ストレージ (VPS) との間で送受信するためのドメインサービスインターフェース。
    """
    def save_training_file(self, uploaded_file: UploadedFileStream, unique_id: str) -> str:
        """
        [Backend向け] 訓練データとしてアップロードされたファイルストリームを保存し、
        ワーカーがアクセスできるリモートパスを返す。
        """
        ...

    def save_training_model(self, model_artifact: UploadedFileStream, unique_id: str) -> str:
        """
        [Backend/Worker向け] 単一の訓練済みモデル成果物を保存し、リモートパスを返す。
        (upload_directory が推奨される場合がある)
        """
        ...

    # --- Worker <-> Storage (Download/Upload) ---

    def download_file(self, remote_path: str, local_path: str) -> None:
        """
        [Worker向け] リモートストレージ上のファイル (remote_path) を
        ローカルファイルシステム (local_path) にダウンロードする。
        """
        ...

    def upload_directory(self, local_dir_path: str, remote_base_dir: str,
                         return_remote_paths: bool = False) -> Dict[str, str]:
        """
        [Worker向け] ローカルディレクトリ (local_dir_path) の内容を
        リモートストレージ上の指定されたベースディレクトリ (remote_base_dir) にアップロードする。

        Args:
            local_dir_path: アップロード元のローカルディレクトリパス。
            remote_base_dir: アップロード先のリモートベースディレクトリパス。
            return_remote_paths: Trueの場合、アップロードされた各ファイルの
                                 ローカル相対パスをキー、リモート絶対パスを値とする辞書を返す。

        Returns:
            Dict[str, str]: return_remote_paths=True の場合、パスのマッピング辞書。それ以外は空辞書。
        """
        ...