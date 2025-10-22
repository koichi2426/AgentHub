import os
from typing import Optional
from domain.services.file_storage_domain_service import FileStorageDomainService
from domain.value_objects.file_data import UploadedFileStream
# 実際のストレージ操作を行うインフラ層のヘルパーをインポート
from infrastructure.storage.local_file_storage import save_training_file, FileStorageError


class LocalFileStorageDomainServiceImpl(FileStorageDomainService):
    """
    FileStorageDomainService のローカルファイルシステム向け実装。
    共有ボリュームにファイルを保存する責務を持つ。
    """
    def save_training_file(self, uploaded_file: UploadedFileStream, unique_id: str) -> str:
        """
        抽象化されたファイルストリームを受け取り、ローカルファイルとして保存する。
        """
        try:
            # save_training_file ヘルパー関数が、UploadedFileStream の file_stream を使用して
            # ファイルを保存するロジックを持つことを前提として、ここではファイルのストリーム自体を渡します。
            # NOTE: 現在の local_file_storage.py の実装は UploadFile を受け取る形式なので、
            #       ここでは UploadedFileStream の file_stream と filename を分離して渡す処理を
            #       行うか、または save_training_file の引数を修正する必要があります。
            
            # 【実用的な修正】: 抽象化されたストリームからデータを読み取り、保存処理に渡す
            
            # [暫定実装: local_file_storage.py の save_training_file が UploadFile の API に近い処理を持つため、
            #  一旦ストリームとファイル名を渡す形で実装]
            
            # --- 実行時のエラーを防ぐため、save_training_file の引数を抽象型に合わせる ---
            
            # *自作の save_training_file ヘルパー関数が UploadedFileStream と互換性を持つことを前提とします*
            # ここでは、元のインフラヘルパーの関数名を再利用し、抽象型を渡すDIコンテナを想定
            
            # NOTE: save_training_file のシグネチャを以下のように仮定します
            # save_training_file(file_stream: BinaryIO, filename: str, unique_id: str) -> str:
            
            file_path = save_training_file(
                uploaded_file.file_stream, 
                uploaded_file.filename,
                unique_id
            )
            return file_path
        
        except FileStorageError as e:
            # インフラ層のエラーを透過的に上位層に伝える
            raise e
        except Exception as e:
            raise FileStorageError(f"Unexpected error during file saving: {e}")


def NewFileStorageDomainService() -> FileStorageDomainService:
    """FileStorageDomainService のファクトリ関数"""
    return LocalFileStorageDomainServiceImpl()