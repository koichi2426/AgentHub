import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
from domain.entities.agent import Agent, AgentRepository # AgentRepositoryを使用
from domain.entities.user import User  # Userエンティティの参照が必要
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetUserAgentsUseCase(Protocol):
    """特定のユーザーが作成した全てのエージェントを取得するユースケースのインターフェース"""
    def execute(
        self, input: "GetUserAgentsInput"
    ) -> Tuple["GetUserAgentsOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class GetUserAgentsInput:
    """ユーザーを特定するための認証トークン"""
    token: str


# ======================================
# Output DTO (内部リスト用)
# ======================================
@dataclass
class AgentListItem:
    """エージェント一覧表示用のDTO"""
    id: int
    user_id: int
    owner: str
    name: str
    description: Optional[str]

# ======================================
# Output DTO (全体)
# ======================================
@dataclass
class GetUserAgentsOutput:
    """エージェントのリストを含む最終的なOutput DTO"""
    agents: List[AgentListItem]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetUserAgentsPresenter(abc.ABC):
    """ドメインエンティティのリストをOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, agents: List[Agent]) -> GetUserAgentsOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetUserAgentsInteractor:
    def __init__(
        self,
        presenter: "GetUserAgentsPresenter",
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
    ):
        self.presenter = presenter
        self.agent_repo = agent_repo
        self.auth_service = auth_service

    def execute(
        self, input: GetUserAgentsInput
    ) -> Tuple["GetUserAgentsOutput", Exception | None]:
        """
        認証トークンからユーザーを特定し、そのユーザーが所有するエージェント一覧を取得する。
        """
        empty_output = GetUserAgentsOutput(agents=[])
        
        try:
            # 1. トークンを検証してユーザー情報を取得
            user: User = self.auth_service.verify_token(input.token)
            
            # 2. AgentRepositoryから特定の user_id に紐づく全てのエージェントを取得
            # 既存のリポジトリメソッド名 (list_by_user_id) を使用
            agents_list: List[Agent] = self.agent_repo.list_by_user_id(user.id)
            
            # 3. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(agents_list)
            return output, None
            
        except Exception as e:
            # エラー時は空のリストを持つDTOと例外を返す
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_user_agents_interactor(
    presenter: "GetUserAgentsPresenter",
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
) -> "GetUserAgentsUseCase":
    return GetUserAgentsInteractor(
        presenter=presenter,
        agent_repo=agent_repo,
        auth_service=auth_service,
    )