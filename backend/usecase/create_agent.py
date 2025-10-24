import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional

from domain.entities.agent import Agent, AgentRepository
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID


# ======================================
# Usecaseのインターフェース定義
# ======================================
class CreateAgentUseCase(Protocol):
    def execute(
        self, input: "CreateAgentInput"
    ) -> Tuple["CreateAgentOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class CreateAgentInput:
    token: str
    name: str
    description: Optional[str]


# ======================================
# Output DTO
# ======================================
@dataclass
class CreateAgentOutput:
    id: int
    user_id: int
    owner: str
    name: str
    description: Optional[str]


# ======================================
# Presenterのインターフェース定義
# ======================================
class CreateAgentPresenter(abc.ABC):
    @abc.abstractmethod
    def output(self, agent: Agent) -> CreateAgentOutput:
        pass


# ======================================
# Usecaseの具体的な実装
# ======================================
class CreateAgentInteractor:
    def __init__(
        self,
        presenter: "CreateAgentPresenter",
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
        timeout_sec: int = 10,
    ):
        self.presenter = presenter
        self.agent_repo = agent_repo
        self.auth_service = auth_service
        self.timeout_sec = timeout_sec

    def execute(
        self, input: CreateAgentInput
    ) -> Tuple["CreateAgentOutput", Exception | None]:
        try:
            # トークンを検証してユーザー情報を取得
            user = self.auth_service.verify_token(input.token)

            # Agentエンティティを生成
            agent_to_create = Agent(
                id=ID(0),  # IDはDBで自動採番される
                user_id=user.id,
                owner=user.username,
                name=input.name,
                description=input.description,
            )

            # リポジトリに永続化を委譲
            created_agent = self.agent_repo.create(agent_to_create)

            # Presenterに渡してOutput DTOに変換
            output = self.presenter.output(created_agent)
            return output, None
            
        except Exception as e:
            # エラー時は空のDTOと例外を返す
            empty_output = CreateAgentOutput(
                id=0, user_id=0, owner="", name="", description=""
            )
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_create_agent_interactor(
    presenter: "CreateAgentPresenter",
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
    timeout_sec: int = 10,
) -> "CreateAgentUseCase":
    return CreateAgentInteractor(
        presenter=presenter,
        agent_repo=agent_repo,
        auth_service=auth_service,
        timeout_sec=timeout_sec,
    )

