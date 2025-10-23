from typing import BinaryIO, Any
from domain.value_objects.file_data import UploadedFileStream


class FastAPIUploadedFileAdapter(UploadedFileStream):
    """
    FastAPIのUploadFileオブジェクトを、ドメイン層のUploadedFileStreamインターフェースに
    適合させるためのアダプタ（インフラ層の実装）。
    """
    def __init__(self, upload_file: Any): 
        # 厳密な型チェックを削除し、ダックタイピング（属性チェック）に移行
        
        # ファイル操作に必要な 'file' と 'filename' 属性があるかを確認
        if not hasattr(upload_file, 'file') or not hasattr(upload_file, 'filename'):
             raise TypeError("Object passed to adapter lacks necessary file stream attributes.")
             
        self._upload_file = upload_file

    @property
    def filename(self) -> str:
        """アップロードされた元のファイル名を返す"""
        # FastAPIのUploadFileのfilenameを参照
        return self._upload_file.filename or ""

    @property
    def content_type(self) -> str:
        """ファイルのMIMEタイプを返す"""
        # FastAPIのUploadFileのcontent_typeを参照
        return self._upload_file.content_type or "application/octet-stream"
        
    @property
    def file_stream(self) -> BinaryIO:
        """ファイルの内容にアクセスするための標準的なファイルストリームを返す"""
        # FastAPIのUploadFileのfile属性（spooled temporary file）を参照
        return self._upload_file.file