import abc
from dataclasses import dataclass
from typing import Protocol, Tuple

from passlib.context import CryptContext

# domain 側の型 / ファクトリをインポート
from domain.entities.user import User, UserRepository, NewUser

# ======================================
# パスワードハッシュ用
# ======================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ======================================
# Usecaseのインターフェース定義
# ======================================
class CreateUserUseCase(Protocol):
    def execute(self, input: "CreateUserInput") -> Tuple["CreateUserOutput", Exception | None]:
        ...


# ======================================
# Input DTO
# ======================================
@dataclass
class CreateUserInput:
    username: str
    name: str
    email: str
    avatar_url: str
    password: str  # 平文で受け取る


# ======================================
# Output DTO
# ======================================
@dataclass
class UserOutputDTO:
    id: int
    username: str
    name: str
    email: str
    avatar_url: str


@dataclass
class CreateUserOutput:
    user: UserOutputDTO


# ======================================
# Presenterのインターフェース定義
# ======================================
class CreateUserPresenter(abc.ABC):
    @abc.abstractmethod
    def output(self, user: User) -> CreateUserOutput:
        pass


# ======================================
# Usecaseの具体的な実装
# ======================================
class CreateUserInteractor:
    def __init__(self, presenter: "CreateUserPresenter", repo: UserRepository, timeout_sec: int = 10):
        self.presenter = presenter
        self.repo = repo
        self.timeout_sec = timeout_sec

    def execute(self, input: CreateUserInput) -> Tuple["CreateUserOutput", Exception | None]:
        try:
            # パスワードをハッシュ化
            hashed_password = pwd_context.hash(input.password)

            # IDはDB側で自動採番される想定なので仮で0をセット
            # domain側の NewUser のシグネチャに合わせて呼び出す
            new_user = NewUser(
                id=0,
                name=input.username,  # domain NewUser は name 引数を username としても利用する実装のためここに username を渡す
                email=input.email,
                password_hash=hashed_password,
                avatar_url=input.avatar_url,
            )

            # 永続化
            created = self.repo.create(new_user)

            # Presenterに渡す
            output = self.presenter.output(created)
            return output, None
        except Exception as e:
            empty_output = CreateUserOutput(
                user=UserOutputDTO(id=0, username="", name="", email="", avatar_url="")
            )
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_create_user_interactor(presenter: "CreateUserPresenter", repo: UserRepository, timeout_sec: int = 10) -> CreateUserUseCase:
    return CreateUserInteractor(presenter=presenter, repo=repo, timeout_sec=timeout_sec)
