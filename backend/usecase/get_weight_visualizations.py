import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List, Any

# ドメイン層の依存関係
from domain.entities.weight_visualization import WeightVisualization, WeightVisualizationRepository
from domain.entities.finetuning_job import FinetuningJobRepository
from domain.entities.agent import AgentRepository
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID


# ======================================
# Usecaseのインターフェース定義
# ======================================
class GetFinetuningJobVisualizationUseCase(Protocol):
    """特定のジョブの重み可視化データを取得するユースケースのインターフェース"""
    def execute(
        self, input: "GetFinetuningJobVisualizationInput"
    ) -> Tuple["GetFinetuningJobVisualizationOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput DTO
# ======================================
@dataclass
class GetFinetuningJobVisualizationInput:
    """ユーザー認証トークンとジョブID"""
    token: str
    job_id: int


# ======================================
# Output DTO (Value Object のリストを JSON フレンドリーに変換)
# ======================================
@dataclass(frozen=True)
class WeightVisualizationDetail:
    name: str
    before_url: str
    after_url: str
    delta_url: str

@dataclass(frozen=True)
class LayerVisualizationOutput:
    layer_name: str
    weights: List[WeightVisualizationDetail]

@dataclass
class GetFinetuningJobVisualizationOutput:
    """可視化データ全体の最終的なOutput DTO"""
    job_id: int
    layers: List[LayerVisualizationOutput]


# ======================================
# Presenterのインターフェース定義
# ======================================
class GetFinetuningJobVisualizationPresenter(abc.ABC):
    """ドメインエンティティをOutput DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, visualization: WeightVisualization) -> GetFinetuningJobVisualizationOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class GetFinetuningJobVisualizationInteractor:
    def __init__(
        self,
        presenter: "GetFinetuningJobVisualizationPresenter",
        vis_repo: WeightVisualizationRepository,
        job_repo: FinetuningJobRepository,
        agent_repo: AgentRepository, # 所有権チェックのために AgentRepository も必要
        auth_service: AuthDomainService,
    ):
        self.presenter = presenter
        self.vis_repo = vis_repo
        self.job_repo = job_repo
        self.agent_repo = agent_repo
        self.auth_service = auth_service

    def execute(
        self, input: GetFinetuningJobVisualizationInput
    ) -> Tuple["GetFinetuningJobVisualizationOutput", Exception | None]:
        
        empty_output = GetFinetuningJobVisualizationOutput(job_id=input.job_id, layers=[])
        
        try:
            # 1. トークンを検証してユーザー情報を取得 (認証)
            user = self.auth_service.verify_token(input.token)
            
            job_id_obj = ID(input.job_id)

            # 2. ジョブの存在確認と所有権チェック (セキュリティ)
            job = self.job_repo.find_by_id(job_id_obj)
            if not job:
                raise ValueError(f"Finetuning Job with ID {input.job_id} not found.")

            # 2a. Agentを取得し、UserがAgentの所有者であることを確認
            agent = self.agent_repo.find_by_id(job.agent_id)
            if not agent or agent.user_id.value != user.id.value:
                 raise PermissionError("User does not have access to this job's data.")
            
            # 3. Visualization Repositoryからデータを取得
            visualization = self.vis_repo.find_by_job_id(job_id_obj)
            
            if not visualization:
                # データが見つからない場合は、エラーではなく空のリストを返す (404ではない)
                return empty_output, None 

            # 4. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(visualization)
            return output, None
            
        except (ValueError, PermissionError) as e:
            # 認証エラー、権限エラー、ジョブが見つからないエラー
            return empty_output, e
        except Exception as e:
            # DBエラーなどのその他のシステムエラー
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_get_finetuning_job_visualization_interactor(
    presenter: "GetFinetuningJobVisualizationPresenter",
    vis_repo: WeightVisualizationRepository,
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
) -> "GetFinetuningJobVisualizationUseCase":
    return GetFinetuningJobVisualizationInteractor(
        presenter=presenter,
        vis_repo=vis_repo,
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
    )
