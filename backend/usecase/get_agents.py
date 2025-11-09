import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
from domain.entities.agent import Agent, AgentRepository 


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetAgentsUseCase(Protocol):
    """現存する全てのアクティブなエージェントを取得するユースケースのインターフェース"""
    def execute(
        self, input: "GetAgentsInput"
    ) -> Tuple["GetAgentsOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# (全件取得であり、認証不要のため空)
# ======================================
@dataclass
class GetAgentsInput:
    """インプットデータは不要だが、インターフェース整合性のため定義"""
    pass


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
class GetAgentsOutput:
    """エージェントのリストを含む最終的なOutput DTO"""
    agents: List[AgentListItem]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetAgentsPresenter(abc.ABC):
    """ドメインエンティティのリストをOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, agents: List[Agent]) -> GetAgentsOutput:
        """AgentエンティティのリストをDTOに変換して返す"""
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetAgentsInteractor:
    """現存する全てのアクティブなエージェント一覧を取得するユースケースの実行処理"""
    def __init__(
        self,
        presenter: GetAgentsPresenter,
        agent_repo: AgentRepository,
    ):
        self.presenter = presenter
        self.agent_repo = agent_repo

    def execute(
        self, input: GetAgentsInput
    ) -> Tuple[GetAgentsOutput, Exception | None]:
        """
        AgentRepositoryからアクティブな全てのエージェント一覧を取得する。
        """
        empty_output = GetAgentsOutput(agents=[])
        
        try:
            # 1. AgentRepositoryから現存する全てのアクティブなエージェントを取得
            agents_list: List[Agent] = self.agent_repo.list_all_active()
            
            # 2. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(agents_list)
            return output, None
            
        except Exception as e:
            # DBアクセスエラーなど、全てのエラーを捕捉
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_agents_interactor(
    presenter: GetAgentsPresenter,
    agent_repo: AgentRepository,
) -> GetAgentsUseCase:
    return GetAgentsInteractor(
        presenter=presenter,
        agent_repo=agent_repo,
    )