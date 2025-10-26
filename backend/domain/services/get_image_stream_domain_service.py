import abc
from typing import Protocol, Tuple
import os
import mimetypes

# 抽象化されたストリーム型をインポート (backend/domain/value_objects/binary_stream.py で定義されたもの)
from domain.value_objects.binary_stream import BinaryStream 

class FileStreamDomainService(Protocol):
    """
    リモートの永続ストレージから、特定のファイルをバイナリストリームとして取得し、
    HTTP配信に利用する責務を持つドメインサービスインターフェース。
    """
    def get_file_stream_by_path(self, relative_path: str) -> Tuple[BinaryStream, str]:
        """
        ファイルパスを受け取り、ファイルの中身をBinaryStreamとして返す。
        
        Args:
            relative_path: VPSの可視化ベースディレクトリに対する相対パス (例: 'job_ID/layer0/image.png')。
            
        Returns:
            Tuple[BinaryStream, str]: ファイルのストリームと、推測されたMIMEタイプ (例: 'image/png')。
            
        Raises:
            Exception: ファイルが見つからない場合や接続エラーが発生した場合。
        """
        ...