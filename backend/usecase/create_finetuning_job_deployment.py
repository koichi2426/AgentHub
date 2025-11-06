import abc
import os  # ★ 環境変数を読み込む
from urllib.parse import urljoin  # ★ URLを安全に結合する
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
# --- 認証・権限チェック用 ---
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository
from domain.entities.agent import Agent, AgentRepository
from domain.entities.user import User
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID
# --- 今回の主役（書き込み対象） ---
from domain.entities.deployment import Deployment, DeploymentRepository


# ======================================
# Usecaseのインターフェース定義
# ======================================
class CreateFinetuningJobDeploymentUseCase(Protocol):
    """
    特定のFinetuning Job IDに紐づくデプロイメントを（1件）作成する
    ユースケースのインターフェース
    """
    def execute(
        self, input: "CreateFinetuningJobDeploymentInput"
    ) -> Tuple["CreateFinetuningJobDeploymentOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class CreateFinetuningJobDeploymentInput:
    """認証トークンと、デプロイ対象のジョブID"""
    token: str
    job_id: int  # プリミティブなintで受け取り、Usecase内でID VOに変換


# ======================================
# Output DTO (内部用)
# ======================================
@dataclass
class CreatedDeploymentDTO:
    """作成されたデプロイメント情報のDTO"""
    id: int
    job_id: int
    status: str       # (例: "inactive")
    endpoint: Optional[str] # (例: "http://...")


# ======================================
# Output DTO (全体)
# ======================================
@dataclass
class CreateFinetuningJobDeploymentOutput:
    """作成されたデプロイメントのDTOを含む最終的なOutput"""
    deployment: CreatedDeploymentDTO


# ======================================
# Presenterのインターフェース定義
# ======================================
class CreateFinetuningJobDeploymentPresenter(abc.ABC):
    """ドメインエンティティ(Deployment)をOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, deployment: Deployment) -> CreateFinetuningJobDeploymentOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class CreateFinetuningJobDeploymentInteractor:
    def __init__(
        self,
        presenter: "CreateFinetuningJobDeploymentPresenter",
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
        
        # C++エンジンのベースURLを環境変数から読み込む
        base_url = os.environ.get("AGENTHUB_ENGINE_BASE_URL")
        if not base_url:
            raise ValueError("AGENTHUB_ENGINE_BASE_URL environment variable is not set.")
        if not base_url.endswith('/'):
            base_url += '/'
        self.engine_base_url = base_url

    def execute(
        self, input: CreateFinetuningJobDeploymentInput
    ) -> Tuple["CreateFinetuningJobDeploymentOutput", Exception | None]:
        """
        トークンでユーザーを認証し、指定されたJob IDの
        デプロイメントを新規作成する。
        """
        
        try:
            # 1. 認証 (Auth)
            user: User = self.auth_service.verify_token(input.token)
            
            # 2. ジョブ取得 (Find Job)
            job_id_vo = ID(input.job_id)
            job: Optional[FinetuningJob] = self.job_repo.find_by_id(job_id_vo)
            
            if job is None:
                raise FileNotFoundError(f"Job {input.job_id} not found.")

            # 3. 権限チェック (Check Permission)
            agent: Optional[Agent] = self.agent_repo.find_by_id(job.agent_id)
            
            if agent is None:
                raise FileNotFoundError(f"Agent {job.agent_id} (for job {job.id}) not found.")
            
            # Agentの`owner`ではなく`user_id`フィールドを参照
            if agent.user_id != user.id:
                raise PermissionError(
                    "User does not have permission to create a deployment for this job."
                )

            # 4. ロジック本体 (Create)
            
            # 4a. 既存デプロイメントのチェック（ジョブ：デプロイ＝1：1 のため）
            existing_deployment = self.deployment_repo.find_by_job_id(job_id_vo)
            if existing_deployment:
                # すでに存在する
                raise FileExistsError(
                    f"Deployment for job {input.job_id} already exists (ID: {existing_deployment.id})."
                )

            # 4b. エンドポイントURLを構築 (例: "http://.../job45/predict")
            job_path = f"job{job_id_vo.value}/"
            predict_endpoint_path = urljoin(job_path, "predict")
            full_endpoint = urljoin(self.engine_base_url, predict_endpoint_path)

            # 4c. 新しいデプロイメントエンティティを準備
            # (IDはリポジトリ(DB)側で採番されることを期待し、ダミーのID(0)をセット)
            new_deployment_data = Deployment(
                id=ID(0), # 採番前ダミーID
                job_id=job_id_vo,
                status="active",
                endpoint=full_endpoint
            )
            
            # 4d. リポジトリに作成を依頼
            created_deployment: Deployment = self.deployment_repo.create(new_deployment_data)
            
            # 5. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(created_deployment)
            return output, None
            
        except Exception as e:
            # エラー時は空のDTOと例外を返す（空のDTOを定義して返す）
            empty_output = CreateFinetuningJobDeploymentOutput(
                deployment=CreatedDeploymentDTO(id=0, job_id=0, status="", endpoint=None)
            )
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_create_finetuning_job_deployment_interactor(
    presenter: "CreateFinetuningJobDeploymentPresenter",
    deployment_repo: DeploymentRepository,
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
) -> "CreateFinetuningJobDeploymentUseCase":
    return CreateFinetuningJobDeploymentInteractor(
        presenter=presenter,
        deployment_repo=deployment_repo,
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
    )