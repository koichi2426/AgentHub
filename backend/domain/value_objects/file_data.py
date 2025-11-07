# backend/domain/value_objects/file_data.py

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

    # ★★★ 修正箇所: 非同期の read() メソッドを追加 ★★★
    @abc.abstractmethod
    async def read(self) -> bytes:
        """
        ファイルの内容全体を非同期で読み込み、バイトデータとして返す。
        （FastAPIの UploadFile.read() に対応）
        """
        pass
    # ★★★ 修正箇所ここまで ★★★