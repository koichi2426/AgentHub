import mysql.connector
from mysql.connector import pooling
from typing import Any, List, Optional

# --- 依存するインターフェースと設定クラスをインポート ---
from adapter.repository.sql import SQL, Tx, Row, Rows, RowData
from infrastructure.database.config import MySQLConfig


# --- Rows / Row インターフェースのMySQL実装 ---

class MySQLRow(Row):
    """
    単一の結果行をラップするクラス。
    """
    def __init__(self, row_data: Optional[RowData]):
        self._row_data = row_data

    def scan(self, *dest: Any) -> None:
        """
        取得した行データを指定された変数に格納する。
        Pythonではこのパターンは稀で、直接タプルとして受け取るのが一般的。
        """
        if self._row_data is None:
            raise ValueError("行が見つかりません")
        
        if len(dest) != len(self._row_data):
            raise ValueError(f"引数の数({len(dest)})とカラムの数({len(self._row_data)})が一致しません")

        # この実装はGoのScanを模倣するためのもので、実際にはあまり使われない
        print(f"警告: scan()は概念的な実装です。")

    # データを直接取得するためのメソッドを追加
    def get_values(self) -> Optional[RowData]:
        return self._row_data


class MySQLRows(Rows):
    """
    複数の結果行（データのリスト）をラップするクラス。
    """
    def __init__(self, rows_data: List[RowData]):
        self._rows_data = rows_data

    def __iter__(self):
        return iter(self._rows_data)

    # カーソルベースのメソッドは不要になる
    def next(self) -> bool:
        return False

    def close(self) -> None:
        pass


# --- Transaction インターフェースのMySQL実装 ---

class MySQLTx(Tx):
    """
    トランザクションをラップするクラス。
    """
    def __init__(self, connection):
        self.conn = connection
        self.conn.start_transaction()
        self.cursor = self.conn.cursor()

    def execute(self, query: str, *params: Any) -> None:
        self.cursor.execute(query, params)

    def query(self, query: str, *params: Any) -> Rows:
        self.cursor.execute(query, params)
        rows_data = self.cursor.fetchall()
        return MySQLRows(rows_data)

    def query_row(self, query: str, *params: Any) -> Row:
        self.cursor.execute(query, params)
        row_data = self.cursor.fetchone()
        return MySQLRow(row_data)

    def commit(self) -> None:
        self.conn.commit()
        self.cursor.close()

    def rollback(self) -> None:
        self.conn.rollback()
        self.cursor.close()


# --- Main SQL インターフェースのMySQL実装 ---

class MySQLHandler(SQL):
    """
    データベース接続全体を管理するハンドラ。
    """
    def __init__(self, config: MySQLConfig):
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mysql_pool",
                pool_size=10,
                user=config.user,
                password=config.password,
                host=config.host,
                port=config.port,
                database=config.database,
                charset='utf8mb4' # 文字化け対策を追加
            )
        except Exception as e:
            print(f"データベース接続に失敗しました: {e}")
            raise

    def _get_connection(self):
        return self.pool.get_connection()

    def _put_connection(self, conn):
        conn.close()

    def execute(self, query: str, *params: Any) -> None:
        """
        INSERT / UPDATE / DELETE を実行する。
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self._put_connection(conn)

    def execute_and_return_id(self, query: str, *params: Any) -> int:
        """
        INSERT を実行し、自動採番された ID を返す。
        """
        conn = self._get_connection()
        last_id = -1
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                last_id = cur.lastrowid
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self._put_connection(conn)
        return last_id

    def query(self, query: str, *params: Any) -> Rows:
        conn = self._get_connection()
        rows_data = []
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows_data = cur.fetchall()
        finally:
            self._put_connection(conn)
        return MySQLRows(rows_data)

    def query_row(self, query: str, *params: Any) -> Row:
        conn = self._get_connection()
        row_data = None
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                row_data = cur.fetchone()
        finally:
            self._put_connection(conn)
        return MySQLRow(row_data)

    def begin_tx(self) -> Tx:
        conn = self._get_connection()
        return MySQLTx(conn)


def NewMySQLHandler(config: MySQLConfig) -> MySQLHandler:
    """
    MySQLHandlerのインスタンスを生成するファクトリ関数。
    """
    return MySQLHandler(config)
