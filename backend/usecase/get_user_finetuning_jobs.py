import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List, Any

# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository 
from domain.entities.user import User  
from domain.services.auth_domain_service import AuthDomainService


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetUserFinetuningJobsUseCase(Protocol):
    """特定のユーザーが所有する全てのエージェントのファインチューニングジョブを取得するユースケースのインターフェース"""
    def execute(
        self, input: "GetUserFinetuningJobsInput"
    ) -> Tuple["GetUserFinetuningJobsOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class GetUserFinetuningJobsInput:
    """ユーザーを特定するための認証トークン"""
    token: str


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
class GetUserFinetuningJobsOutput:
    """ジョブのリストを含む最終的なOutput DTO"""
    jobs: List[FinetuningJobListItem]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetUserFinetuningJobsPresenter(abc.ABC):
    """ドメインエンティティのリストをOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, jobs: List[FinetuningJob]) -> GetUserFinetuningJobsOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetUserFinetuningJobsInteractor:
    def __init__(
        self,
        presenter: "GetUserFinetuningJobsPresenter",
        job_repo: FinetuningJobRepository, # FinetuningJobRepositoryを使用
        auth_service: AuthDomainService,
    ):
        self.presenter = presenter
        self.job_repo = job_repo
        self.auth_service = auth_service

    def execute(
        self, input: GetUserFinetuningJobsInput
    ) -> Tuple["GetUserFinetuningJobsOutput", Exception | None]:
        
        empty_output = GetUserFinetuningJobsOutput(jobs=[])
        
        try:
            # 1. トークンを検証してユーザー情報を取得
            user: User = self.auth_service.verify_token(input.token)
            
            # 2. JobRepositoryから特定の user_id に紐づく全てのジョブを取得
            # FinetuningJobRepository に list_all_by_user メソッドが存在することを前提とする
            jobs_list: List[FinetuningJob] = self.job_repo.list_all_by_user(user.id)
            
            # 3. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(jobs_list)
            return output, None
            
        except Exception as e:
            # エラー時は空のリストを持つDTOと例外を返す
            import traceback; traceback.print_exc()
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_user_finetuning_jobs_interactor(
    presenter: "GetUserFinetuningJobsPresenter",
    job_repo: FinetuningJobRepository,
    auth_service: AuthDomainService,
) -> "GetUserFinetuningJobsUseCase":
    return GetUserFinetuningJobsInteractor(
        presenter=presenter,
        job_repo=job_repo,
        auth_service=auth_service,
    )