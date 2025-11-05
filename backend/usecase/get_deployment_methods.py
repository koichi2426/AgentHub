import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
# --- 認証・権限チェック用 ---
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository
from domain.entities.agent import Agent, AgentRepository
from domain.entities.user import User
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID
# --- 今回の主役（取得対象） ---
from domain.entities.deployment import Deployment, DeploymentRepository
from domain.entities.methods import DeploymentMethods, DeploymentMethodsRepository
from domain.value_objects.method import Method


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetDeploymentMethodsUseCase(Protocol):
    """
    特定のDeployment IDに紐づくメソッド（機能）を取得する
    ユースケースのインターフェース
    """
    def execute(
        self, input: "GetDeploymentMethodsInput"
    ) -> Tuple["GetDeploymentMethodsOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class GetDeploymentMethodsInput:
    """認証トークンと、対象のデプロイメントID"""
    token: str
    deployment_id: int


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
class GetDeploymentMethodsOutput:
    """メソッドのリストを含む最終的なOutput DTO"""
    deployment_id: int
    methods: List[MethodListItemDTO]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetDeploymentMethodsPresenter(abc.ABC):
    """ドメインエンティティ(DeploymentMethods)をOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, methods_entity: DeploymentMethods) -> GetDeploymentMethodsOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetDeploymentMethodsInteractor:
    def __init__(
        self,
        presenter: "GetDeploymentMethodsPresenter",
        methods_repo: DeploymentMethodsRepository,
        deployment_repo: DeploymentRepository,
        job_repo: FinetuningJobRepository,
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
    ):
        self.presenter = presenter
        self.methods_repo = methods_repo
        self.deployment_repo = deployment_repo
        self.job_repo = job_repo
        self.agent_repo = agent_repo
        self.auth_service = auth_service

    def execute(
        self, input: GetDeploymentMethodsInput
    ) -> Tuple["GetDeploymentMethodsOutput", Exception | None]:
        """
        トークンでユーザーを認証し、指定されたDeployment IDの
        メソッド（機能）リストを取得する。
        """
        
        try:
            # 1. 認証 (Auth)
            user: User = self.auth_service.verify_token(input.token)
            
            # 2. デプロイメント取得 (Find Deployment)
            deployment_id_vo = ID(input.deployment_id)
            deployment: Optional[Deployment] = self.deployment_repo.find_by_id(deployment_id_vo)
            
            if deployment is None:
                raise FileNotFoundError(f"Deployment {input.deployment_id} not found.")

            # 3. 権限チェック (Check Permission) - 逆引き
            # 3a. Deployment -> Job
            job: Optional[FinetuningJob] = self.job_repo.find_by_id(deployment.job_id)
            if job is None:
                raise FileNotFoundError(f"Job {deployment.job_id} (for deployment {deployment.id}) not found.")

            # 3b. Job -> Agent
            agent: Optional[Agent] = self.agent_repo.find_by_id(job.agent_id)
            if agent is None:
                raise FileNotFoundError(f"Agent {job.agent_id} (for job {job.id}) not found.")
            
            # 3c. Agent.owner ?= User
            if agent.owner_id != user.id:
                raise PermissionError(
                    "User does not have permission to access this deployment's methods."
                )

            # 4. ロジック本体 (Find Methods)
            # 権限OK。Deployment ID でメソッドを探す
            methods_list: List[Method] = []
            deployment_methods: Optional[DeploymentMethods] = self.methods_repo.find_by_deployment_id(deployment_id_vo)
            
            if deployment_methods:
                methods_list = deployment_methods.methods
            
            # 5. Presenterに渡してOutput DTOに変換
            #    (PresenterのI/Fが DeploymentMethods を要求するので、
            #     見つからなかった場合はダミーを渡すか、I/Fを変更する必要がある)
            
            if deployment_methods is None:
                # 見つからなかった場合、空のエンティティを作って渡す
                deployment_methods = DeploymentMethods(
                    id=ID(0), 
                    deployment_id=deployment_id_vo, 
                    methods=[]
                )

            output = self.presenter.output(deployment_methods)
            return output, None
            
        except Exception as e:
            # エラー時は空のDTOと例外を返す
            empty_output = GetDeploymentMethodsOutput(
                deployment_id=input.deployment_id, methods=[]
            )
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_deployment_methods_interactor(
    presenter: "GetDeploymentMethodsPresenter",
    methods_repo: DeploymentMethodsRepository,
    deployment_repo: DeploymentRepository,
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
) -> "GetDeploymentMethodsUseCase":
    return GetDeploymentMethodsInteractor(
        presenter=presenter,
        methods_repo=methods_repo,
        deployment_repo=deployment_repo,
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
    )