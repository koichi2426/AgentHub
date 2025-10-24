import abc
from typing import Protocol, Optional

# ドメイン層の抽象ファイルオブジェクトをインポート
from domain.value_objects.file_data import UploadedFileStream 

class FileStorageDomainService(Protocol):
    """
    トレーニングファイルを永続ストレージに保存するドメインサービスインターフェース。
    ユースケース層から利用され、具体的なストレージ実装はインフラ層に委譲される。
    """
    def save_training_file(self, uploaded_file: UploadedFileStream, unique_id: str) -> str:
        """
        アップロードされたファイルストリームを保存し、ワーカーがアクセスできるパスを返す。

        Args:
            uploaded_file: ドメイン層の抽象ファイルストリームオブジェクト。
            unique_id: ファイル名の一意性を確保するためのID（例: Agent ID）。

        Returns:
            str: 永続化されたファイルの絶対パス。
        """
        ...