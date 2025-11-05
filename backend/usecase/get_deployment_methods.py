import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJobRepository
from domain.entities.agent import AgentRepository
from domain.entities.user import User
from domain.services.auth_domain_service import AuthDomainService
from domain.services.job_method_finder_domain_service import JobMethodFinderDomainService # HTTPサービス
from domain.value_objects.id import ID
from domain.value_objects.method import Method


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
    job_id: int  # ★ 修正: job_id を追加


# ======================================
# Output DTO
# ======================================
@dataclass
class GetDeploymentMethodsOutput:
    methods: List[str]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetDeploymentMethodsPresenter(abc.ABC):
    @abc.abstractmethod
    def output(self, methods: List[str]) -> GetDeploymentMethodsOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetDeploymentMethodsInteractor:
    def __init__(
        self,
        presenter: "GetDeploymentMethodsPresenter",
        job_method_finder_service: JobMethodFinderDomainService,
        job_repo: FinetuningJobRepository,
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
    ):
        self.presenter = presenter
        self.job_method_finder_service = job_method_finder_service
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

            # 3. ロジック本体: C++エンジンからメソッドを取得
            # job_method_finder_service は HTTP クライアントとして動作
            method_vos: List[Method] = self.job_method_finder_service.find_methods_by_job_id(job_id_vo)
            
            # 4. Presenterに渡すために文字列リストに変換
            method_names = [vo.name for vo in method_vos]
            
            # 5. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(method_names)
            return output, None
            
        except Exception as e:
            # エラー時は空のDTOと例外を返す
            empty_output = GetDeploymentMethodsOutput(methods=[])
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_deployment_methods_interactor(
    presenter: "GetDeploymentMethodsPresenter",
    job_method_finder_service: JobMethodFinderDomainService,
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
) -> "GetDeploymentMethodsUseCase":
    return GetDeploymentMethodsInteractor(
        presenter=presenter,
        job_method_finder_service=job_method_finder_service,
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
    )