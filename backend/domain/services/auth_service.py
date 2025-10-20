import abc
from typing import Optional

from ..entities.user import User


class AuthService(abc.ABC):
    @abc.abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        認証情報を検証し、認証に成功すれば User を返す
        """
        pass

    @abc.abstractmethod
    def hash_password(self, plain: str) -> str:
        """
        パスワードをハッシュ化して返す
        """
        pass

    @abc.abstractmethod
    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        平文とハッシュを検証する
        """
        pass
