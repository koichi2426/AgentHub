import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
from domain.entities.deployment import Deployment, DeploymentRepository
from domain.entities.agent import Agent, AgentRepository 
from domain.entities.user import User  
from domain.value_objects.id import ID 
from domain.services.auth_domain_service import AuthDomainService


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetAgentDeploymentsUseCase(Protocol):
    """特定のAgentに紐づくデプロイメント一覧を取得するユースケースのインターフェース"""
    def execute(
        self, input: "GetAgentDeploymentsInput"
    ) -> Tuple["GetAgentDeploymentsOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class GetAgentDeploymentsInput:
    """ユーザーを特定するための認証トークンと、対象AgentのID"""
    token: str
    agent_id: int 


# ======================================
# Output DTO (内部リスト用)
# ======================================
@dataclass
class DeploymentListItem:
    """デプロイメント一覧表示用のDTO（Deploymentエンティティのフラット化）"""
    id: int
    job_id: int
    status: str
    endpoint: Optional[str]


# ======================================
# Output DTO (全体)
# ======================================
@dataclass
class GetAgentDeploymentsOutput:
    """デプロイメントのリストを含む最終的なOutput DTO"""
    deployments: List[DeploymentListItem]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetAgentDeploymentsPresenter(abc.ABC):
    """ドメインエンティティのリストをOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, deployments: List[Deployment]) -> GetAgentDeploymentsOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetAgentDeploymentsInteractor:
    def __init__(
        self,
        presenter: "GetAgentDeploymentsPresenter",
        deployment_repo: DeploymentRepository, # ★ デプロイメント取得用
        agent_repo: AgentRepository, # ★ 権限チェック用
        auth_service: AuthDomainService,
    ):
        self.presenter = presenter
        self.deployment_repo = deployment_repo
        self.agent_repo = agent_repo
        self.auth_service = auth_service

    def execute(
        self, input: GetAgentDeploymentsInput
    ) -> Tuple["GetAgentDeploymentsOutput", Exception | None]:
        
        empty_output = GetAgentDeploymentsOutput(deployments=[])
        
        try:
            # 1. トークンを検証してユーザー情報を取得
            user: User = self.auth_service.verify_token(input.token)
            agent_id_vo = ID(input.agent_id)
            
            # 2. 権限チェック: このAgentをユーザーが所有しているか確認
            agent: Optional[Agent] = self.agent_repo.find_by_id(agent_id_vo)
            
            if agent is None:
                raise FileNotFoundError(f"Agent {input.agent_id} not found.")

            if agent.user_id != user.id:
                raise PermissionError(
                    "User does not have permission to access this agent's deployments."
                )
            
            # 3. 権限OK。DeploymentRepositoryから特定の agent_id に紐づく全てのデプロイメントを取得
            # DeploymentRepository に list_by_agent(agent_id_vo) が存在することを前提とする
            deployments_list: List[Deployment] = self.deployment_repo.list_by_agent(agent_id_vo)
            
            # 4. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(deployments_list)
            return output, None
            
        except Exception as e:
            # エラー時は空のリストを持つDTOと例外を返す
            import traceback; traceback.print_exc()
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_agent_deployments_interactor(
    presenter: "GetAgentDeploymentsPresenter",
    deployment_repo: DeploymentRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
) -> "GetAgentDeploymentsUseCase":
    return GetAgentDeploymentsInteractor(
        presenter=presenter,
        deployment_repo=deployment_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
    )