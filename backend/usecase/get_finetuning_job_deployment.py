import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
# --- 今回必要になるリポジトリ群 ---
from domain.entities.deployment import Deployment, DeploymentRepository
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository
from domain.entities.agent import Agent, AgentRepository 
# --- 認証サービスとエンティティ ---
from domain.entities.user import User
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID


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
    job_id: int


# ======================================
# Output DTO (単一デプロイメント用)
# ======================================
# 修正1a: DeploymentListItem の代わりに、フロントエンドの Fetch DTO に合わせる
@dataclass
class GetFinetuningJobDeploymentOutput:
    """単一のデプロイメント情報を含む最終的なOutput DTO"""
    # 修正1b: id を追加し、Presenterが要求する全てのフィールドを定義
    id: int
    finetuning_job_id: int # job_id の代わりに finetuning_job_id を使用
    status: str
    endpoint: Optional[str]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetFinetuningJobDeploymentPresenter(abc.ABC):
    """ドメインエンティティ(Deployment)をOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    # 修正2: リストではなく単一のDeploymentエンティティを受け取る
    def output(self, deployment: Deployment) -> GetFinetuningJobDeploymentOutput:
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
        # 修正3: 空のDTOを定義（単一オブジェクトを返すため）
        empty_deployment_dto = GetFinetuningJobDeploymentOutput(
            id=0, finetuning_job_id=0, status="", endpoint=None
        )
        
        try:
            # 1. トークンを検証してユーザー情報を取得
            user: User = self.auth_service.verify_token(input.token)
            
            # 2. Job IDからジョブ情報を取得
            job_id_vo = ID(input.job_id)
            job: Optional[FinetuningJob] = self.job_repo.find_by_id(job_id_vo)
            
            if job is None:
                raise FileNotFoundError(f"Job {input.job_id} not found.")

            # 3. 権限チェック：
            agent: Optional[Agent] = self.agent_repo.find_by_id(job.agent_id)
            
            if agent is None:
                raise FileNotFoundError(f"Agent {job.agent_id} (for job {job.id}) not found.")
            
            if agent.user_id != user.id:
                raise PermissionError(
                    "User does not have permission to access this job's deployment."
                )

            # 4. 権限OK。Job IDに紐づくデプロイメントを取得
            # 修正4: リポジトリのfind_by_job_idは単一のOptional[Deployment]を返すことを想定
            deployment: Optional[Deployment] = self.deployment_repo.find_by_job_id(job_id_vo)
            
            if deployment is None:
                raise FileNotFoundError(f"Deployment for job {input.job_id} not found.")
                
            # 5. Presenterに渡してOutput DTOに変換
            # 修正5: 単一のDeploymentエンティティを渡す
            output = self.presenter.output(deployment)
            return output, None
            
        except Exception as e:
            # エラー時は空のDTOと例外を返す
            return empty_deployment_dto, e


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