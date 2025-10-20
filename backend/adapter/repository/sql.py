import abc
from typing import Any, Iterable, List, Optional, Protocol, Sequence, Tuple, TypeVar

# --- 基本的な型定義 ---

# データベースから返されるプリミティブな値の型
Primitive = Optional[str | int | float | bool | bytes]

# 1行のデータを表す型。タプルやシーケンスを想定。
RowData = Sequence[Primitive]

# --- Rows / Row インターフェース ---

class Rows(Protocol):
    """
    複数の結果行を扱うためのインターフェース。
    Goの `sql.Rows` に相当し、PythonのDB-APIにおけるカーソルのように振る舞う。
    """

    def scan(self, *dest: Any) -> None:
        """GoのScanのように、現在の行のデータを引数に格納する（Pythonではあまり使われない）"""
        ...

    def next(self) -> bool:
        """次の行に進む。行がなければFalseを返す。"""
        ...

    def err(self) -> Optional[Exception]:
        """イテレーション中に発生したエラーを返す。"""
        ...

    def close(self) -> None:
        """結果セットを閉じる。"""
        ...

    def fetchone(self) -> Optional[RowData]:
        """次の1行を取得する。"""
        ...

    def fetchall(self) -> List[RowData]:
        """残りのすべての行を取得する。"""
        ...

    def __iter__(self) -> Iterable[RowData]:
        """イテレータとして自身を返す。"""
        ...

class Row(Protocol):
    """
    単一の結果行を扱うためのインターフェース。
    Goの `sql.Row` に相当する。
    """

    def scan(self, *dest: Any) -> None:
        """
        行のデータを引数に格納する。
        データが存在しない、またはエラーが発生した場合は例外を発生させる。
        """
        ...

# --- Transaction インターフェース ---

class Tx(abc.ABC):
    """
    トランザクションを扱うためのインターフェース。
    Goの `sql.Tx` に相当する。
    """

    @abc.abstractmethod
    def execute(self, query: str, *params: Any) -> None:
        """結果を返さないクエリ（INSERT, UPDATE, DELETEなど）を実行する。"""
        pass

    @abc.abstractmethod
    def query(self, query: str, *params: Any) -> Rows:
        """複数の行を返すクエリを実行する。"""
        pass

    @abc.abstractmethod
    def query_row(self, query: str, *params: Any) -> Row:
        """最大で1行を返すクエリを実行する。"""
        pass

    @abc.abstractmethod
    def commit(self) -> None:
        """トランザクションをコミットする。"""
        pass

    @abc.abstractmethod
    def rollback(self) -> None:
        """トランザクションをロールバックする。"""
        pass

# --- Main SQL インターフェース ---

class SQL(abc.ABC):
    """
    データベース操作の全体を担うインターフェース。
    Goの `sql.DB` に相当する。
    """

    @abc.abstractmethod
    def execute(self, query: str, *params: Any) -> None:
        """結果を返さないクエリ（INSERT, UPDATE, DELETEなど）を実行する。"""
        pass

    @abc.abstractmethod
    def query(self, query: str, *params: Any) -> Rows:
        """複数の行を返すクエリを実行する。"""
        pass

    @abc.abstractmethod
    def query_row(self, query: str, *params: Any) -> Row:
        """最大で1行を返すクエリを実行する。"""
        pass

    @abc.abstractmethod
    def begin_tx(self) -> Tx:
        """トランザクションを開始する。"""
        pass