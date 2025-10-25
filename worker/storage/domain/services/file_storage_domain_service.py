import abc
from typing import Protocol, Optional

from domain.value_objects.file_data import UploadedFileStream 

class FileStorageDomainService(Protocol):
    """
    トレーニングファイルおよび訓練モデルを永続ストレージに保存するドメインサービスインターフェース。
    具体的なストレージ実装はインフラ層に委譲される。
    """
    def save_training_file(self, uploaded_file: UploadedFileStream, unique_id: str) -> str:
        """
        訓練データとしてアップロードされたファイルストリームを保存し、ワーカーがアクセスできるパスを返す。

        Args:
            uploaded_file: 抽象ファイルストリームオブジェクト。
            unique_id: ファイル名の一意性を確保するためのID（例: Agent ID）。

        Returns:
            str: 永続化されたファイルの絶対パス。
        """
        ...
        
    def save_training_model(self, model_artifact: UploadedFileStream, unique_id: str) -> str:
        """
        訓練済みモデルの成果物（アーティファクト）を保存し、デプロイワーカーがアクセスできるパスを返す。

        Args:
            model_artifact: 訓練済みモデルのデータストリームを持つ抽象オブジェクト。
            unique_id: モデルを特定するための一意なID（例: Agent ID、または Agent ID + Version）。

        Returns:
            str: 永続化されたモデルファイルの絶対パス。
        """
        ...