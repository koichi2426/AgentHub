import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
# --- 今回必要になるリポジトリ群 ---
# パスは仮定
from domain.entities.deployment import Deployment, DeploymentRepository
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository
from domain.entities.agent import Agent, AgentRepository 
# --- 認証サービスとエンティティ ---
from domain.entities.user import User
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID
# --- 権限エラーは標準の PermissionError を使用 ---


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetFinetuningJobDeploymentUseCase(Protocol):
    """
    特定のFinetuning Job IDに紐づくデプロイメントを取得する
    ユースケースのインターフェース
    """
    def execute(
        self, input: "GetFinetuningJobDeploymentInput"
    ) -> Tuple["GetFinetuningJobDeploymentOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class GetFinetuningJobDeploymentInput:
    """認証トークンと、対象のジョブID"""
    token: str
    job_id: int  # プリミティブなintで受け取り、Usecase内でID VOに変換


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
class GetFinetuningJobDeploymentOutput:
    """デプロイメントのリストを含む最終的なOutput DTO"""
    deployments: List[DeploymentListItem]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetFinetuningJobDeploymentPresenter(abc.ABC):
    """ドメインエンティティ(Deployment)のリストをOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, deployments: List[Deployment]) -> GetFinetuningJobDeploymentOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetFinetuningJobDeploymentInteractor:
    def __init__(
        self,
        presenter: "GetFinetuningJobDeploymentPresenter",
        deployment_repo: DeploymentRepository,
        job_repo: FinetuningJobRepository,
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
    ):
        self.presenter = presenter
        self.deployment_repo = deployment_repo
        self.job_repo = job_repo
        self.agent_repo = agent_repo
        self.auth_service = auth_service

    def execute(
        self, input: GetFinetuningJobDeploymentInput
    ) -> Tuple["GetFinetuningJobDeploymentOutput", Exception | None]:
        """
        トークンでユーザーを認証し、指定されたJob IDの
        デプロイメントを取得する。
        """
        empty_output = GetFinetuningJobDeploymentOutput(deployments=[])
        
        try:
            # 1. トークンを検証してユーザー情報を取得
            user: User = self.auth_service.verify_token(input.token)
            
            # 2. Job IDからジョブ情報を取得
            job_id_vo = ID(input.job_id)
            job: Optional[FinetuningJob] = self.job_repo.find_by_id(job_id_vo)
            
            if job is None:
                raise FileNotFoundError(f"Job {input.job_id} not found.")

            # 3. 権限チェック：
            #    そのジョブが所属するエージェントを、このユーザーが所有しているか？
            agent: Optional[Agent] = self.agent_repo.find_by_id(job.agent_id)
            
            if agent is None:
                raise FileNotFoundError(f"Agent {job.agent_id} (for job {job.id}) not found.")
            
            # Agentエンティティの定義に従い、user_id属性を使用
            if agent.user_id != user.id:
                raise PermissionError( # 標準のPermissionErrorを使用
                    "User does not have permission to access this job's deployment."
                )
            # ▲▲▲ 修正箇所 ▲▲▲

            # 4. 権限OK。Job IDに紐づくデプロイメントを取得
            deployments_list: List[Deployment] = self.deployment_repo.find_by_job_id(job_id_vo)
            
            # 5. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(deployments_list)
            return output, None
            
        except Exception as e:
            # エラー時は空のリストを持つDTOと例外を返す
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_finetuning_job_deployment_interactor(
    presenter: "GetFinetuningJobDeploymentPresenter",
    deployment_repo: DeploymentRepository,
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
) -> "GetFinetuningJobDeploymentUseCase":
    return GetFinetuningJobDeploymentInteractor(
        presenter=presenter,
        deployment_repo=deployment_repo,
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
    )