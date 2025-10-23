import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, Any

# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository
from domain.entities.agent import AgentRepository
from domain.services.auth_domain_service import AuthDomainService
# 新しい抽象ドメインサービス
from domain.services.file_storage_domain_service import FileStorageDomainService
from domain.services.job_queue_domain_service import JobQueueDomainService
from domain.services.system_time_domain_service import SystemTimeDomainService
from domain.value_objects.id import ID
from domain.value_objects.file_data import UploadedFileStream 


# ======================================
# Usecaseのインターフェース定義
# ======================================
class CreateFinetuningJobUseCase(Protocol):
    def execute(
        self, input: "CreateFinetuningJobInput"
    ) -> Tuple["CreateFinetuningJobOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class CreateFinetuningJobInput:
    token: str
    agent_id: int
    training_file: UploadedFileStream # 抽象型を使用


# ======================================
# Output DTO
# ======================================
@dataclass
class CreateFinetuningJobOutput:
    id: int
    agent_id: int
    status: str
    created_at: str
    message: str = "Job successfully queued."


# ======================================
# Presenterのインターフェース定義
# ======================================
class CreateFinetuningJobPresenter(abc.ABC):
    @abc.abstractmethod
    def output(self, job: FinetuningJob) -> CreateFinetuningJobOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class CreateFinetuningJobInteractor:
    def __init__(
        self,
        presenter: "CreateFinetuningJobPresenter",
        job_repo: FinetuningJobRepository,
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
        file_storage_service: FileStorageDomainService, 
        job_queue_service: JobQueueDomainService,
        system_time_service: SystemTimeDomainService, 
    ):
        self.presenter = presenter
        self.job_repo = job_repo
        self.agent_repo = agent_repo
        self.auth_service = auth_service
        self.file_storage_service = file_storage_service 
        self.job_queue_service = job_queue_service       
        self.system_time_service = system_time_service 

    def execute(
        self, input: CreateFinetuningJobInput
    ) -> Tuple["CreateFinetuningJobOutput", Exception | None]:
        
        empty_output = CreateFinetuningJobOutput(id=0, agent_id=0, status="", created_at="", message="")
        
        try:
            print("# 1. トークンを検証してユーザー情報を取得")
            user = self.auth_service.verify_token(input.token)

            print("# 2. Agentの存在確認と所有権チェック")
            agent = self.agent_repo.find_by_id(ID(input.agent_id))
            if not agent:
                raise ValueError(f"Agent with ID {input.agent_id} not found.")
            if agent.user_id.value != user.id.value:
                raise PermissionError("User does not own this agent.")
                
            # 3. ファイルを抽象サービスに委譲して共有ストレージに保存
            print("# 3. ファイルを抽象サービスに委譲して共有ストレージに保存")
            file_path = self.file_storage_service.save_training_file(
                input.training_file, 
                str(input.agent_id)
            )

            # ★ 4a. 時刻サービスの利用 ★
            # 時刻をインフラ層から文字列で取得
            print("# 4a. 時刻サービスの利用")
            current_time_str = self.system_time_service.get_current_time()
            
            # 4b. FinetuningJobエンティティを生成（初期ステータス: 'queued'）
            print("# 4b. FinetuningJobエンティティを生成")
            new_job = FinetuningJob(
                id=ID(0), 
                agent_id=ID(input.agent_id),
                training_file_path=file_path,
                status="queued",
                model_id=None,
                # created_at には、時刻サービスから取得した純粋な文字列を渡す
                created_at=current_time_str, 
                finished_at=None,
                error_message=None
            )

            print("# 5. リポジトリにジョブを永続化")
            created_job = self.job_repo.create_job(new_job)

            print("# 6. 抽象的なキューサービスを通じてタスクをキューに投入")
            self.job_queue_service.enqueue_finetuning_job(
                created_job.id.value, 
                created_job.training_file_path
            )

            print("# 7. Presenterに渡してOutput DTOに変換")
            output = self.presenter.output(created_job)
            return output, None
            
        except (ValueError, PermissionError) as e:
            # ファイル保存失敗や認証/権限エラー
            import traceback; traceback.print_exc()
            return empty_output, e
        except Exception as e:
            # その他のシステムエラー
            import traceback; traceback.print_exc()
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_create_finetuning_job_interactor(
    presenter: "CreateFinetuningJobPresenter",
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
    file_storage_service: FileStorageDomainService,
    job_queue_service: JobQueueDomainService,
    system_time_service: SystemTimeDomainService,
) -> "CreateFinetuningJobUseCase":
    return CreateFinetuningJobInteractor(
        presenter=presenter,
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
        file_storage_service=file_storage_service,
        job_queue_service=job_queue_service,
        system_time_service=system_time_service,
    )