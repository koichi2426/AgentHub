from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from domain.entities.user import User, UserRepository
from domain.services.auth_domain_service import AuthDomainService

# --- .env から設定を読み込む ---
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # デフォルトは安全でないので必ず設定
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# パスワードハッシュ用
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthDomainServiceImpl(AuthDomainService):
    """
    JWT を利用した認証ドメインサービスの具体的実装
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login(self, email: str, password: str) -> str:
        """
        メールアドレスとパスワードを検証し、JWT トークンを発行する。
        """
        user: Optional[User] = self._find_user_by_email(email)
        if not user:
            raise ValueError("User not found")

        if not pwd_context.verify(password, user.password):
            raise ValueError("Invalid credentials")

        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user.id), "exp": expire}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    def verify_token(self, token: str) -> User:
        """
        JWT を検証して、対応する User を返す。
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise ValueError("Invalid token: no subject")

            user = self.user_repo.find_by_id(int(user_id))
            if not user:
                raise ValueError("User not found")
            return user
        except JWTError:
            raise ValueError("Invalid or expired token")

    def logout(self, token: str) -> None:
        """
        ログアウト処理。
        JWT 方式ではサーバー側で状態を持たないため、
        実際の処理は不要（フロントがトークンを破棄するだけ）。
        """
        return None

    # --- 内部ユーティリティ ---
    def _find_user_by_email(self, email: str) -> Optional[User]:
        """
        UserRepository に専用メソッドが無いので find_all で探す。
        """
        users = self.user_repo.find_all()
        for u in users:
            if u.email == email:
                return u
        return None


# --- ファクトリ関数 ---
def NewAuthDomainService(user_repo: UserRepository) -> AuthDomainServiceImpl:
    return AuthDomainServiceImpl(user_repo)
