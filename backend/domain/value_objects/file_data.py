import abc
from typing import BinaryIO, Optional

class UploadedFileStream(abc.ABC):
    """
    ファイルアップロードデータを抽象的に表現するドメイン層のインターフェース。
    ユースケースはこの抽象型のみを参照する。
    """
    @property
    @abc.abstractmethod
    def filename(self) -> str:
        """アップロードされた元のファイル名"""
        pass

    @property
    @abc.abstractmethod
    def content_type(self) -> Optional[str]:
        """ファイルのMIMEタイプ"""
        pass

    @property
    @abc.abstractmethod
    def file_stream(self) -> BinaryIO:
        """ファイルの内容にアクセスするための標準的なバイナリストリーム"""
        pass