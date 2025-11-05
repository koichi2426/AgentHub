import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List, Any

# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository 
from domain.entities.user import User  
from domain.entities.agent import Agent, AgentRepository 
from domain.value_objects.id import ID 
from domain.services.auth_domain_service import AuthDomainService


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetAgentFinetuningJobsUseCase(Protocol):
    """特定のAgentに紐づくファインチューニングジョブ一覧を取得するユースケースのインターフェース"""
    def execute(
        self, input: "GetAgentFinetuningJobsInput"
    ) -> Tuple["GetAgentFinetuningJobsOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class GetAgentFinetuningJobsInput:
    """ユーザーを特定するための認証トークンと、対象AgentのID"""
    token: str
    agent_id: int 


# ======================================
# Output DTO (内部リスト用)
# ======================================
@dataclass
class FinetuningJobListItem:
    """ファインチューニングジョブ一覧表示用のDTO"""
    id: int
    agent_id: int
    status: str
    training_file_path: str
    created_at: str # ISO 8601 string
    finished_at: Optional[str] # ISO 8601 string
    error_message: Optional[str]

# ======================================
# Output DTO (全体)
# ======================================
@dataclass
class GetAgentFinetuningJobsOutput:
    """ジョブのリストを含む最終的なOutput DTO"""
    jobs: List[FinetuningJobListItem]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetAgentFinetuningJobsPresenter(abc.ABC):
    """ドメインエンティティのリストをOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, jobs: List[FinetuningJob]) -> GetAgentFinetuningJobsOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetAgentFinetuningJobsInteractor:
    def __init__(
        self,
        presenter: "GetAgentFinetuningJobsPresenter",
        job_repo: FinetuningJobRepository,
        auth_service: AuthDomainService,
        agent_repo: AgentRepository,
    ):
        self.presenter = presenter
        self.job_repo = job_repo
        self.auth_service = auth_service
        self.agent_repo = agent_repo

    def execute(
        self, input: GetAgentFinetuningJobsInput
    ) -> Tuple["GetAgentFinetuningJobsOutput", Exception | None]:
        
        empty_output = GetAgentFinetuningJobsOutput(jobs=[])
        
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
                    "User does not have permission to access this agent's jobs."
                )
            
            # 3. JobRepositoryから特定の agent_id に紐づく全てのジョブを取得
            # ⬇️⬇️⬇️ 修正箇所：メソッド名を 'list_by_agent' に修正 ⬇️⬇️⬇️
            jobs_list: List[FinetuningJob] = self.job_repo.list_by_agent(agent_id_vo)
            # ⬆️⬆️⬆️ 修正箇所 ⬆️⬆️⬆️
            
            # 4. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(jobs_list)
            return output, None
            
        except Exception as e:
            # エラー時は空のリストを持つDTOと例外を返す
            import traceback; traceback.print_exc()
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_agent_finetuning_jobs_interactor(
    presenter: "GetAgentFinetuningJobsPresenter",
    job_repo: FinetuningJobRepository,
    auth_service: AuthDomainService,
    agent_repo: AgentRepository,
) -> "GetAgentFinetuningJobsUseCase":
    return GetAgentFinetuningJobsInteractor(
        presenter=presenter,
        job_repo=job_repo,
        auth_service=auth_service,
        agent_repo=agent_repo,
    )