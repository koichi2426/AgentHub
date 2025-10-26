import abc
from typing import Protocol, BinaryIO

class BinaryStream(Protocol):
    """
    リモートからダウンロードされた画像データなど、バイナリをメモリ上に保持し、
    ストリーミング配信に必要な操作を保証する抽象型。(io.BytesIO のドメイン層の代替)
    """
    def seek(self, offset: int, whence: int = 0) -> int:
        """ストリームのポインタを移動する（配信開始時のリセットに必要）"""
        ...
    def read(self, size: int = -1) -> bytes:
        """ストリームからバイトデータを読み取る"""
        ...
    def close(self) -> None:
        """ストリームを閉じる"""
        ...
    
    # Pythonのファイルライクオブジェクトとしての振る舞い（context manager）を保証
    def __enter__(self) -> 'BinaryStream':
        """コンテキストマネージャとしてストリームを開く"""
        ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """コンテキストマネージャとしてストリームを閉じる"""
        ...
