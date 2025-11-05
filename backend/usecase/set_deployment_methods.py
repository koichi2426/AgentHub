import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository
from domain.entities.agent import Agent, AgentRepository
from domain.entities.user import User
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID
from domain.entities.deployment import Deployment, DeploymentRepository
from domain.entities.methods import DeploymentMethods, DeploymentMethodsRepository
from domain.value_objects.method import Method
# --- ロジックの核 ---
from domain.services.job_method_finder_domain_service import JobMethodFinderDomainService


# ======================================
# Usecaseのインターフェース定義
# ======================================
class SetDeploymentMethodsUseCase(Protocol):
    """
    特定のデプロイメントに紐づくメソッド（機能）を
    （上書き）設定するユースケースのインターフェース
    """
    def execute(
        self, input: "SetDeploymentMethodsInput"
    ) -> Tuple["SetDeploymentMethodsOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class SetDeploymentMethodsInput:
    """認証トークンと、対象のジョブID"""
    token: str
    job_id: int        # このジョブIDから「登録すべきメソッド」をサービスが探す


# ======================================
# Output DTO (内部リスト用)
# ======================================
@dataclass
class MethodListItemDTO:
    """メソッド一覧表示用のDTO"""
    name: str

# ======================================
# Output DTO (全体)
# ======================================
@dataclass
class SetDeploymentMethodsOutput:
    """（上書き）設定されたメソッドリストのDTOを含む最終的なOutput"""
    deployment_id: int
    methods: List[MethodListItemDTO]


# ======================================
# Presenterのインターフェース定義
# ======================================
class SetDeploymentMethodsPresenter(abc.ABC):
    """ドメインエンティティ(DeploymentMethods)をOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, methods_entity: DeploymentMethods) -> SetDeploymentMethodsOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class SetDeploymentMethodsInteractor:
    def __init__(
        self,
        presenter: "SetDeploymentMethodsPresenter",
        methods_repo: DeploymentMethodsRepository,
        deployment_repo: DeploymentRepository,
        job_repo: FinetuningJobRepository,
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
        method_finder_service: JobMethodFinderDomainService
    ):
        self.presenter = presenter
        self.methods_repo = methods_repo
        self.deployment_repo = deployment_repo
        self.job_repo = job_repo
        self.agent_repo = agent_repo
        self.auth_service = auth_service
        self.method_finder_service = method_finder_service

    def execute(
        self, input: SetDeploymentMethodsInput
    ) -> Tuple["SetDeploymentMethodsOutput", Exception | None]:
        """
        トークンでユーザーを認証し、指定されたJob IDから
        「登録すべきメソッド」をサービスで検索し、
        デプロイメントに紐づけて（上書き）保存する。
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
            
            if agent.user_id != user.id:
                raise PermissionError(
                    "User does not have permission to set methods for this job."
                )
            # ▲▲▲ 修正箇所 ▲▲▲

            # 4. 親となるデプロイメントを取得
            # 注: find_by_job_idはリストを返す可能性があるため、ここでは単一のデプロイメントを想定
            deployments: List[Deployment] = self.deployment_repo.find_by_job_id(job_id_vo)
            deployment: Optional[Deployment] = deployments[0] if deployments else None
            
            if deployment is None:
                raise FileNotFoundError(
                    f"Deployment for job {input.job_id} not found. Create deployment first."
                )

            # 5. ロジック本体 (Find & Save Methods)
            
            # 5a. ドメインサービスを使って「登録すべきメソッド」を取得
            method_vos: List[Method] = self.method_finder_service.find_methods_by_job_id(job_id_vo)
            
            # 5b. 既存のメソッドエンティティを探す
            existing_methods: Optional[DeploymentMethods] = self.methods_repo.find_by_deployment_id(deployment.id)

            if existing_methods:
                # 存在する場合：更新（上書き）
                existing_methods.methods = method_vos
                methods_to_save = existing_methods
            else:
                # 存在しない場合：新規作成
                # DeploymentMethodsエンティティのIDはリポジトリが採番することを期待
                methods_to_save = DeploymentMethods(
                    id=ID(0), # 採番前ダミーID
                    deployment_id=deployment.id,
                    methods=method_vos
                )
            
            # 5c. リポジトリに保存（作成または更新）を依頼
            saved_methods: DeploymentMethods = self.methods_repo.save(methods_to_save)

            # 6. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(saved_methods)
            return output, None
            
        except Exception as e:
            empty_output = SetDeploymentMethodsOutput(
                deployment_id=0, methods=[]
            )
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_set_deployment_methods_interactor(
    presenter: "SetDeploymentMethodsPresenter",
    methods_repo: DeploymentMethodsRepository,
    deployment_repo: DeploymentRepository,
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
    method_finder_service: JobMethodFinderDomainService
) -> "SetDeploymentMethodsUseCase":
    return SetDeploymentMethodsInteractor(
        presenter=presenter,
        methods_repo=methods_repo,
        deployment_repo=deployment_repo,
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
        method_finder_service=method_finder_service
    )