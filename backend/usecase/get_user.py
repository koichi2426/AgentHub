import abc
from dataclasses import dataclass
from typing import Protocol, Tuple
from domain.services.auth_domain_service import AuthDomainService
from domain.entities.user import User

# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetUserUseCase(Protocol):
    def execute(
        self, input: "GetUserInput"
    ) -> Tuple["GetUserOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class GetUserInput:
    token: str


# ======================================
# Output DTO
# ======================================
@dataclass
class GetUserOutput:
    id: int
    username: str
    name: str
    email: str
    avatar_url: str


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetUserPresenter(abc.ABC):
    @abc.abstractmethod
    def output(self, user: User) -> GetUserOutput:
        pass


# ======================================
# Usecaseの具体的な実装
# ======================================
class GetUserInteractor:
    def __init__(
        self,
        presenter: "GetUserPresenter",
        auth_service: AuthDomainService,
        timeout_sec: int = 10,
    ):
        self.presenter = presenter
        self.auth_service = auth_service
        self.timeout_sec = timeout_sec

    def execute(
        self, input: GetUserInput
    ) -> Tuple["GetUserOutput", Exception | None]:
        try:
            # ドメインサービスにトークン検証とユーザー取得を委譲
            user = self.auth_service.verify_token(input.token)

            # PresenterにUserエンティティを渡してOutput DTOを生成
            output = self.presenter.output(user)
            return output, None
        except Exception as e:
            # トークンが無効、期限切れ、またはユーザーが見つからない場合など
            return GetUserOutput(id=0, username="", name="", email="", avatar_url=""), e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_user_interactor(
    presenter: "GetUserPresenter",
    auth_service: AuthDomainService,
    timeout_sec: int = 10,
) -> "GetUserUseCase":
    return GetUserInteractor(
        presenter=presenter,
        auth_service=auth_service,
        timeout_sec=timeout_sec,
    )
