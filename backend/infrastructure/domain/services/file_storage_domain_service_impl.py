import os
from typing import Optional
from domain.services.file_storage_domain_service import FileStorageDomainService
from domain.value_objects.file_data import UploadedFileStream
# 実際のストレージ操作を行うヘルパーはモックのため不要だが、インポートは残す
from infrastructure.storage.local_file_storage import save_training_file, FileStorageError


class MockFileStorageDomainServiceImpl(FileStorageDomainService):
    """
    FileStorageDomainService のモック実装。
    ファイルを保存せず、ダミーのパスを返す。
    """
    def save_training_file(self, uploaded_file: UploadedFileStream, unique_id: str) -> str:
        """
        訓練データファイルを保存する代わりに、ダミーのファイルパスを生成して返す。
        """
        # ファイル保存ロジックの代わりに、ダミーのパスを返す
        # このパスはワーカーが読み込もうとする場所と形式的に一致している必要がある
        dummy_path = f"/data/training/{unique_id}_{uploaded_file.filename}"
        
        # 実際にファイルを保存しないため、処理は常に成功として扱う
        print(f"INFO: File saving mocked. Using path: {dummy_path}")
        
        return dummy_path

    def save_training_model(self, model_artifact: UploadedFileStream, unique_id: str) -> str:
        """
        訓練モデルファイルを保存する代わりに、ダミーのファイルパスを生成して返す。
        """
        # ファイル保存ロジックの代わりに、ダミーのモデルパスを返す
        # データファイルとは異なるディレクトリ構成を想定 (例: /models/)
        dummy_path = f"/data/models/{unique_id}_{model_artifact.filename}"
        
        # 実際にファイルを保存しないため、処理は常に成功として扱う
        print(f"INFO: Model saving mocked. Using path: {dummy_path}")
        
        return dummy_path


def NewFileStorageDomainService() -> FileStorageDomainService:
    """FileStorageDomainService のファクトリ関数"""
    return MockFileStorageDomainServiceImpl()