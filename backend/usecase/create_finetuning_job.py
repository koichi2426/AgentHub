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
        
        # (Job IDを先に取得するため、一時的なジョブを保持する変数を定義)
        temp_job_created: Optional[FinetuningJob] = None
        
        try:
            # 1. トークンを検証してユーザー情報を取得
            user = self.auth_service.verify_token(input.token)

            # 2. Agentの存在確認と所有権チェック
            agent = self.agent_repo.find_by_id(ID(input.agent_id))
            if not agent:
                raise ValueError(f"Agent with ID {input.agent_id} not found.")
            if agent.user_id.value != user.id.value:
                raise PermissionError("User does not own this agent.")
                
            # 3. 時刻サービスの利用
            current_time_str = self.system_time_service.get_current_time()
            
            # 4. FinetuningJobエンティティを「プレ生成」
            new_job_placeholder = FinetuningJob(
                id=ID(0), 
                agent_id=ID(input.agent_id),
                training_file_path="pending_job_id", 
                status="creating",                  
                created_at=current_time_str, 
                finished_at=None,
                error_message=None
            )

            # 5. リポジトリにジョブを「先に」永続化し、IDを取得
            created_job = self.job_repo.create_job(new_job_placeholder)
            temp_job_created = created_job # (ロールバック用に保持)
            job_id_str = str(created_job.id.value) # (これが欲しかったID)

            # 6. 取得した Job ID を使って、ファイルを抽象サービスに委譲
            file_path = self.file_storage_service.save_training_file(
                input.training_file, 
                job_id_str # (ご要望の Job ID を使用)
            )

            # 7. ジョブのファイルパスとステータスを更新
            created_job.training_file_path = file_path
            created_job.status = "queued" # (ここで 'queued' にする)
            
            # リポジトリの更新メソッドを呼び出す
            updated_job = self.job_repo.update_job(created_job) 

            # 8. 抽象的なキューサービスを通じてタスクをキューに投入
            self.job_queue_service.enqueue_finetuning_job(
                updated_job.id.value, 
                updated_job.training_file_path
            )

            # 9. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(updated_job)
            return output, None
            
        except Exception as e:
            # エラー処理: もしファイル保存(6)やジョブ更新(7)に失敗した場合
            # 先に作成したジョブ(5)のステータスを 'failed' に更新する
            if temp_job_created:
                print(f"ERROR: Rolling back job status for job ID {temp_job_created.id.value} due to: {e}")
                temp_job_created.status = "failed"
                temp_job_created.error_message = str(e)
                # エラー状態もDBに反映
                self.job_repo.update_job(temp_job_created) 

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