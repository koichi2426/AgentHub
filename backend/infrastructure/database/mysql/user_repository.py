import mysql.connector
from mysql.connector import pooling
from typing import Optional, List
from contextlib import contextmanager

# ---------------------------------------------------------------------------
# (重要)
# 必要なライブラリをインストールしてください:
# pip install mysql-connector-python
# ---------------------------------------------------------------------------

# --- ドメイン層からのインポート ---
# <--- 修正: 相対パス(....)から絶対パス(domain.)に変更 ---
from domain.entities.user import User, UserRepository
from domain.value_objects.id import ID
from domain.value_objects.email import Email
# <--- 修正: value_objectsも絶対パスに変更 ---

# --- インフラ層（同一階層）からのインポート ---
from .config import MySQLConfig


class MySQLUserRepository(UserRepository):
    """
    UserRepositoryのMySQL実装クラス。
    接続プーリングを使用してデータベースとのやり取りを管理する。
    """

    def __init__(self, config: MySQLConfig):
        """
        設定情報を受け取り、データベース接続プールを初期化する。
        """
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="user_repo_pool",
                pool_size=5,  # プールサイズは環境に合わせて調整
                pool_reset_session=True,
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database=config.database
            )
        except mysql.connector.Error as err:
            print(f"Error initializing connection pool: {err}")
            raise

    # --- 前提 ---
    # 以下のValue Objectは `.value` 属性でプリミティブ値にアクセスできると仮定します。
    # - ID(id).value -> int
    # - Email(email).value -> str
    # もし異なる場合は、`.value` の部分を適宜修正してください。
    #
    # また、DBテーブルは 'users' とし、
    # カラムは (id, username, name, email, avatar_url, password_hash)
    # であると仮定します。
    # ---

    @contextmanager
    def _get_cursor(self, commit: bool = False):
        """
        接続とカーソルを管理するコンテキストマネージャ。
        
        Args:
            commit (bool): トランザクションをコミットするかどうか。
        """
        conn = None
        cursor = None
        try:
            # プールから接続を取得
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()  # エラー時はロールバック
            print(f"Database error: {err}")
            raise  # エラーを再スローして上位層に通知
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()  # 接続をプールに返却

    def _map_row_to_user(self, row: tuple) -> Optional[User]:
        """
        DBの行（タプル）をUserドメインエンティティにマッピングする。
        
        Note:
        `user.py` の `NewUser` ファクトリは `name` を `username` にも
        設定するロジックになっているため、DBからの再構成には不向きと判断し、
        Userコンストラクタを直接呼び出しています。
        """
        if not row:
            return None
        
        # (id, username, name, email, avatar_url, password_hash) の順序を想定
        return User(
            id=ID(row[0]),
            username=row[1],
            name=row[2],
            email=Email(row[3]),
            avatar_url=row[4],
            password_hash=row[5]
        )

    def create(self, user: User) -> User:
        """
        ユーザーを新規作成し、DBが採番したIDを含むUserオブジェクトを返す。
        """
        sql = """
        INSERT INTO users (username, name, email, avatar_url, password_hash)
        VALUES (%s, %s, %s, %s, %s)
        """
        # Value Objectからプリミティブ値を取り出す
        data = (
            user.username,
            user.name,
            user.email.value,  # .value と仮定
            user.avatar_url,
            user.password_hash
        )

        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            new_id = cursor.lastrowid  # AUTO_INCREMENTで設定されたIDを取得

        # 採番されたIDで新しいUserインスタンスを作成して返す
        return User(
            id=ID(new_id),
            username=user.username,
            name=user.name,
            email=user.email,
            avatar_url=user.avatar_url,
            password_hash=user.password_hash
        )

    def find_by_id(self, user_id: "ID") -> Optional[User]:
        """
        IDからユーザーを検索する。
        """
        sql = "SELECT id, username, name, email, avatar_url, password_hash FROM users WHERE id = %s"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (user_id.value,))  # .value と仮定
            row = cursor.fetchone()
        
        return self._map_row_to_user(row)

    def find_by_username(self, username: str) -> Optional[User]:
        """
        ユーザー名からユーザーを検索する。
        """
        sql = "SELECT id, username, name, email, avatar_url, password_hash FROM users WHERE username = %s"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            
        return self._map_row_to_user(row)

    def find_all(self) -> List[User]:
        """
        すべてのユーザーを取得する。
        """
        sql = "SELECT id, username, name, email, avatar_url, password_hash FROM users ORDER BY id"
        with self._get_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            
        return [self._map_row_to_user(row) for row in rows if row]

    def update(self, user: User) -> None:
        """
        ユーザー情報を更新する。
        """
        sql = """
        UPDATE users
        SET username = %s, name = %s, email = %s, avatar_url = %s, password_hash = %s
        WHERE id = %s
        """
        data = (
            user.username,
            user.name,
            user.email.value,  # .value と仮定
            user.avatar_url,
            user.password_hash,
            user.id.value        # .value と仮定
        )
        
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            if cursor.rowcount == 0:
                # 0件更新は、対象IDが存在しなかったことを意味する（エラーとはしない）
                print(f"Warning: Update for user ID {user.id.value} affected 0 rows.")

    def delete(self, user_id: "ID") -> None:
        """
        IDでユーザーを削除する。
        """
        sql = "DELETE FROM users WHERE id = %s"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, (user_id.value,))  # .value と仮定
            if cursor.rowcount == 0:
                print(f"Warning: Delete for user ID {user_id.value} affected 0 rows.")

    def delete_all(self) -> None:
        """
        すべてのユーザーを削除する。
        """
        sql = "DELETE FROM users"
        # TRUNCATE TABLE users; の方が高速だが、
        # トランザクション制御やトリガーの観点からDELETEが安全な場合がある
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql)