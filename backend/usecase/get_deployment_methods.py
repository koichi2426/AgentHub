import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJobRepository
from domain.entities.agent import AgentRepository
from domain.entities.user import User
from domain.services.auth_domain_service import AuthDomainService
from domain.services.job_method_finder_domain_service import JobMethodFinderDomainService 
from domain.value_objects.id import ID
from domain.value_objects.method import Method

# ★★★ 修正箇所1: メソッドとデプロイメントのリポジトリをインポート ★★★
from domain.entities.deployment import Deployment, DeploymentRepository
from domain.entities.methods import DeploymentMethods, DeploymentMethodsRepository


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetDeploymentMethodsUseCase(Protocol):
    def execute(
        self, input: "GetDeploymentMethodsInput"
    ) -> Tuple["GetDeploymentMethodsOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class GetDeploymentMethodsInput:
    """認証トークンと、メソッドを取得する対象のJob ID"""
    token: str
    job_id: int


# ======================================
# Output DTO (Presenterと整合させるために追加)
# ======================================
@dataclass
class MethodListItemDTO:
    """メソッド一覧表示用のDTO"""
    name: str

@dataclass
class GetDeploymentMethodsOutput:
    # ⬇️⬇️⬇️ 修正箇所1: deployment_id を追加 ⬇️⬇️⬇️
    deployment_id: int 
    # ⬆️⬆️⬆️ 修正箇所1 ⬆️⬆️⬆️
    methods: List[MethodListItemDTO]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetDeploymentMethodsPresenter(abc.ABC):
    @abc.abstractmethod
    # ⬇️⬇️⬇️ 修正箇所2: deployment_id も引数として渡すように変更 ⬇️⬇️⬇️
    def output(self, deployment_id: int, methods: List[Method]) -> GetDeploymentMethodsOutput:
        pass
    # ⬆️⬆️⬆️ 修正箇所2 ⬆️⬆️⬆️


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetDeploymentMethodsInteractor:
    def __init__(
        self,
        presenter: "GetDeploymentMethodsPresenter",
        # 修正2a: HTTPサービスを削除
        # job_method_finder_service: JobMethodFinderDomainService,
        
        # 修正2b: メソッドリポジトリとデプロイメントリポジトリを追加
        methods_repo: DeploymentMethodsRepository,
        deployment_repo: DeploymentRepository,
        
        job_repo: FinetuningJobRepository,
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
    ):
        self.presenter = presenter
        # self.job_method_finder_service = job_method_finder_service # 削除
        
        self.methods_repo = methods_repo # 追加
        self.deployment_repo = deployment_repo # 追加
        
        self.job_repo = job_repo
        self.agent_repo = agent_repo
        self.auth_service = auth_service

    def execute(
        self, input: GetDeploymentMethodsInput
    ) -> Tuple["GetDeploymentMethodsOutput", Exception | None]:
        
        try:
            # 1. 認証 (Auth)
            user: User = self.auth_service.verify_token(input.token)
            job_id_vo = ID(input.job_id)
            
            # 2. 権限チェックのためにジョブとエージェントを取得
            job = self.job_repo.find_by_id(job_id_vo)
            if job is None:
                raise FileNotFoundError(f"Job {input.job_id} not found.")

            agent = self.agent_repo.find_by_id(job.agent_id)
            if agent is None:
                raise FileNotFoundError(f"Agent {job.agent_id} not found.")
            
            if agent.user_id != user.id:
                raise PermissionError(
                    "User does not have permission to view methods for this job."
                )

            # ★★★ 修正3: ロジック本体 - リポジトリから取得 ★★★
            
            # 3a. デプロイメントIDを取得
            deployment: Optional[Deployment] = self.deployment_repo.find_by_job_id(job_id_vo)
            
            if deployment is None:
                method_vos = [] # デプロイメントがない場合はメソッドもない
                deployment_id_value = 0 # IDがない場合はダミー値
            else:
                deployment_id_value = deployment.id.value # IDオブジェクトから値を取得
                # 3b. デプロイメントIDからメソッドエンティティを取得
                methods_entity: Optional[DeploymentMethods] = self.methods_repo.find_by_deployment_id(deployment.id)

                if methods_entity is None:
                    method_vos = [] # 設定がない場合は空
                else:
                    method_vos = methods_entity.methods # Value Objectのリストを取得

            # 4. Presenterに Value Object のリストと ID を渡す
            # ⬇️⬇️⬇️ 修正箇所3: deployment_id を Presenter に渡す ⬇️⬇️⬇️
            output = self.presenter.output(deployment_id_value, method_vos) 
            # ⬆️⬆️⬆️ 修正箇所3 ⬆️⬆️⬆️
            return output, None
            
        except Exception as e:
            # エラー時は空のDTOと例外を返す
            # ⬇️⬇️⬇️ 修正箇所4: エラー時の Output DTO にも deployment_id を追加 ⬇️⬇️⬇️
            empty_output = GetDeploymentMethodsOutput(deployment_id=0, methods=[])
            # ⬆️⬆️⬆️ 修正箇所4 ⬆️⬆️⬆️
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_deployment_methods_interactor(
    presenter: "GetDeploymentMethodsPresenter",
    # 修正4a: HTTPサービスを削除
    # job_method_finder_service: JobMethodFinderDomainService,
    
    # 修正4b: メソッドリポジトリとデプロイメントリポジトリを追加
    methods_repo: DeploymentMethodsRepository,
    deployment_repo: DeploymentRepository,
    
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
) -> "GetDeploymentMethodsUseCase":
    return GetDeploymentMethodsInteractor(
        presenter=presenter,
        # job_method_finder_service=job_method_finder_service, # 削除
        
        methods_repo=methods_repo, # 追加
        deployment_repo=deployment_repo, # 追加
        
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
    )