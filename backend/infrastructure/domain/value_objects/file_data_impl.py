# backend/infrastructure/domain/value_objects/file_data_impl.py

from typing import BinaryIO, Any, Optional
from domain.value_objects.file_data import UploadedFileStream
import asyncio 

class FastAPIUploadedFileAdapter(UploadedFileStream):
    """
    FastAPIのUploadFileオブジェクトを、ドメイン層のUploadedFileStreamインターフェースに
    適合させるためのアダプタ（インフラ層の実装）。
    """
    def __init__(self, upload_file: Any): 
        # ファイル操作に必要な属性があるかを確認
        if not hasattr(upload_file, 'file') or not hasattr(upload_file, 'filename'):
             raise TypeError("Object passed to adapter lacks necessary file stream attributes.")
             
        self._upload_file = upload_file

    @property
    def filename(self) -> str:
        """アップロードされた元のファイル名を返す"""
        return self._upload_file.filename or ""

    @property
    def content_type(self) -> Optional[str]:
        """ファイルのMIMEタイプを返す"""
        return self._upload_file.content_type or None
        
    @property
    def file_stream(self) -> BinaryIO:
        """ファイルの内容にアクセスするための標準的なファイルストリームを返す"""
        return self._upload_file.file
        
    # ★★★ 修正箇所: 欠落していた非同期の read() メソッドを実装 ★★★
    async def read(self) -> bytes:
        """
        ファイルの内容全体を非同期で読み込み、バイトデータとして返す。
        """
        # FastAPIの UploadFile.read() は非同期メソッド
        return await self._upload_file.read() 
    # ★★★ 修正箇所ここまで ★★★