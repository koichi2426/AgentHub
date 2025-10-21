import abc
from dataclasses import dataclass
from typing import Protocol, Tuple
from domain.services.auth_domain_service import AuthDomainService

# ======================================
# Usecaseのインターフェース定義
# ======================================
class LoginUserUseCase(Protocol):
    def execute(
        self, input: "LoginUserInput"
    ) -> Tuple["LoginUserOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class LoginUserInput:
    email: str
    password: str


# ======================================
# Output DTO
# ======================================
@dataclass
class LoginUserOutput:
    token: str


# ======================================
# Presenterのインターフェース定義
# ======================================
class LoginUserPresenter(abc.ABC):
    @abc.abstractmethod
    def output(self, token: str) -> LoginUserOutput:
        pass


# ======================================
# Usecaseの具体的な実装
# ======================================
class LoginUserInteractor:
    def __init__(
        self,
        presenter: "LoginUserPresenter",
        auth_service: AuthDomainService,
        timeout_sec: int = 10,
    ):
        self.presenter = presenter
        self.auth_service = auth_service
        self.timeout_sec = timeout_sec

    def execute(
        self, input: LoginUserInput
    ) -> Tuple["LoginUserOutput", Exception | None]:
        try:
            # ドメインサービスに認証を委譲
            token = self.auth_service.login(input.email, input.password)

            # Presenterに渡す
            output = self.presenter.output(token)
            return output, None
        except Exception as e:
            return LoginUserOutput(token=""), e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_login_user_interactor(
    presenter: "LoginUserPresenter",
    auth_service: AuthDomainService,
    timeout_sec: int = 10, # タイムアウトのデフォルト値を追加
) -> "LoginUserUseCase":
    return LoginUserInteractor(
        presenter=presenter,
        auth_service=auth_service,
        timeout_sec=timeout_sec,
    )
