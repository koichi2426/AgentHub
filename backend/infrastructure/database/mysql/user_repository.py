import mysql.connector
from mysql.connector import pooling
from typing import Optional, List
from contextlib import contextmanager

from domain.entities.user import User, UserRepository
from domain.value_objects.id import ID
from domain.value_objects.email import Email

from .config import MySQLConfig


class MySQLUserRepository(UserRepository):

    def __init__(self, config: MySQLConfig):
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="user_repo_pool",
                pool_size=5,
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

    @contextmanager
    def _get_cursor(self, commit: bool = False):
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            print(f"Database error: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _map_row_to_user(self, row: tuple) -> Optional[User]:
        if not row:
            return None
        
        return User(
            id=ID(row[0]),
            username=row[1],
            name=row[2],
            email=Email(row[3]),
            avatar_url=row[4],
            password_hash=row[5]
        )

    def create(self, user: User) -> User:
        sql = """
        INSERT INTO users (username, name, email, avatar_url, password_hash)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = (
            user.username,
            user.name,
            user.email.value,
            user.avatar_url,
            user.password_hash
        )

        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            new_id = cursor.lastrowid

        return User(
            id=ID(new_id),
            username=user.username,
            name=user.name,
            email=user.email,
            avatar_url=user.avatar_url,
            password_hash=user.password_hash
        )

    def find_by_id(self, user_id: "ID") -> Optional[User]:
        sql = "SELECT id, username, name, email, avatar_url, password_hash FROM users WHERE id = %s"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (user_id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_user(row)

    def find_by_username(self, username: str) -> Optional[User]:
        sql = "SELECT id, username, name, email, avatar_url, password_hash FROM users WHERE username = %s"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            
        return self._map_row_to_user(row)

    def find_by_email(self, email: "Email") -> Optional[User]:
        sql = "SELECT id, username, name, email, avatar_url, password_hash FROM users WHERE email = %s"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (email.value,))
            row = cursor.fetchone()
            
        return self._map_row_to_user(row)

    def find_all(self) -> List[User]:
        sql = "SELECT id, username, name, email, avatar_url, password_hash FROM users ORDER BY id"
        with self._get_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            
        return [self._map_row_to_user(row) for row in rows if row]

    def update(self, user: User) -> None:
        sql = """
        UPDATE users
        SET username = %s, name = %s, email = %s, avatar_url = %s, password_hash = %s
        WHERE id = %s
        """
        data = (
            user.username,
            user.name,
            user.email.value,
            user.avatar_url,
            user.password_hash,
            user.id.value
        )
        
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)

    def delete(self, user_id: "ID") -> None:
        sql = "DELETE FROM users WHERE id = %s"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, (user_id.value,))

    def delete_all(self) -> None:
        sql = "DELETE FROM users"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql)