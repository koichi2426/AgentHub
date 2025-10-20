import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID
from ..value_objects.email import Email


@dataclass
class User:
    id: ID
    username: str
    name: str
    email: Email
    avatar_url: str
    password_hash: str  # 本来はハッシュ化したパスワードを想定


class UserRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, user: User) -> User:
        """
        ユーザーを新規作成し、作成されたUserを返す
        """
        pass

    @abc.abstractmethod
    def find_by_id(self, user_id: "ID") -> Optional[User]:
        """
        IDからユーザーを検索する
        """
        pass

    @abc.abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """
        ユーザー名からユーザーを検索する
        """
        pass

    @abc.abstractmethod
    def find_all(self) -> list[User]:
        """
        すべてのユーザーを取得する
        """
        pass

    @abc.abstractmethod
    def update(self, user: User) -> None:
        """
        ユーザー情報を更新する
        """
        pass

    @abc.abstractmethod
    def delete(self, user_id: "ID") -> None:
        """
        IDでユーザーを削除する
        """
        pass

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        すべてのユーザーを削除する
        """
        pass


def NewUser(
    id: int,
    name: str,
    email: str,
    password_hash: str,
    avatar_url: str,
) -> "User":
    # 互換性のため引数はプリミティブを受け取り内部で VO を生成する
    return User(
        id=ID(id),
        username=name,
        name=name,
        email=Email(email),
        avatar_url=avatar_url,
        password_hash=password_hash,
    )
