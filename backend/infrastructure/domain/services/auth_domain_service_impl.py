from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from domain.entities.user import User, UserRepository
from domain.services.auth_domain_service import AuthDomainService
# --- ▼ 修正: Value Objectをインポート ▼ ---
from domain.value_objects.email import Email
from domain.value_objects.id import ID
# --- ▲ 修正 ▲ ---

# --- .env から設定を読み込む ---
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
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
        # --- ▼ 修正: email(str)を渡す（内部でVOに変換） ▼ ---
        user: Optional[User] = self._find_user_by_email(email)
        # --- ▲ 修正 ▲ ---
        
        if not user:
            raise ValueError("User not found")

        # --- ▼ 修正: password_hash を user オブジェクトから取得 ▼ ---
        if not pwd_context.verify(password, user.password_hash):
            raise ValueError("Invalid credentials")
        # --- ▲ 修正 ▲ ---

        # --- ▼ 修正: user.id (IDオブジェクト) を .value でプリミティブ値に変換 ▼ ---
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user.id.value), "exp": expire} 
        # --- ▲ 修正 ▲ ---
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    def verify_token(self, token: str) -> User:
        """
        JWT を検証して、対応する User を返す。
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_str = payload.get("sub")
            if user_id_str is None:
                raise ValueError("Invalid token: no subject")

            # --- ▼ 修正: str -> int -> ID(VO) の順に変換してリポジトリに渡す ▼ ---
            try:
                user_id_vo = ID(int(user_id_str))
            except ValueError:
                raise ValueError("Invalid user ID in token")
                
            user = self.user_repo.find_by_id(user_id_vo)
            # --- ▲ 修正 ▲ ---
            
            if not user:
                raise ValueError("User not found")
            return user
        except JWTError:
            raise ValueError("Invalid or expired token")

    def logout(self, token: str) -> None:
        """
        ログアウト処理。
        """
        return None

    # --- 内部ユーティリティ ---
    def _find_user_by_email(self, email_str: str) -> Optional[User]:
        # --- ▼ 修正: find_all() をやめて、find_by_email() を使う ▼ ---
        """
        UserRepository の find_by_email を使用して効率的に検索する。
        """
        try:
            # 1. str を Email(VO) に変換
            email_vo = Email(email_str)
            # 2. リポジトリの find_by_email を呼び出す
            return self.user_repo.find_by_email(email_vo)
        except ValueError:
            # Email(VO) のバリデーション（形式チェックなど）でエラーになった場合
            return None
        # --- ▲ 修正 ▲ ---


# --- ファクトリ関数 ---
def NewAuthDomainService(user_repo: UserRepository) -> AuthDomainServiceImpl:
    return AuthDomainServiceImpl(user_repo)