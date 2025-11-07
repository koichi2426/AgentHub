import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List, Dict, Any

# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJob, FinetuningJobRepository
from domain.entities.agent import Agent, AgentRepository
from domain.entities.user import User
from domain.services.auth_domain_service import AuthDomainService
from domain.value_objects.id import ID
from domain.entities.deployment import Deployment, DeploymentRepository
from domain.value_objects.file_data import UploadedFileStream 

# --- 新しいドメインサービスとV.O. ---
from domain.services.deployment_test_domain_service import DeploymentTestDomainService
from domain.value_objects.deployment_test_result import DeploymentTestResult 
from domain.value_objects.test_run_metrics import TestRunMetrics 
from domain.value_objects.inference_case_result import InferenceCaseResult 


# ======================================
# Usecaseのインターフェース定義
# ======================================
class TestDeploymentInferenceUseCase(Protocol):
    """
    デプロイされたモデルに対して、テストファイルを使って同期的に推論テストを実行するユースケース。
    """
    # 修正: execute メソッドを非同期 (async) に変更
    async def execute(
        self, input: "TestDeploymentInferenceInput"
    ) -> Tuple["TestDeploymentInferenceOutput", Exception | None]:
        ...


# ======================================
# UsecaseのInput
# ======================================
@dataclass
class TestDeploymentInferenceInput:
    """認証トークン、対象のデプロイメントID、およびテストデータファイル"""
    token: str
    deployment_id: int 
    test_file: UploadedFileStream


# ======================================
# Output DTO (内部リスト用 - 最終レスポンス形式に合わせる)
# ======================================
@dataclass
class TestMetricsOutput:
    """評価メトリクスと詳細結果を含むDTO"""
    overall_metrics: Dict[str, Any] 
    case_results: List[Dict[str, Any]] 

# ======================================
# Output DTO (全体)
# ======================================
@dataclass
class TestDeploymentInferenceOutput:
    """テスト実行結果とメッセージを含む最終的なOutput"""
    test_result: TestMetricsOutput
    message: str = "Test run successfully." # メッセージを修正


# ======================================
# Presenterのインターフェース定義
# ======================================
class TestDeploymentInferencePresenter(abc.ABC):
    """DeploymentTestResult V.O. を Output DTOに変換するPresenter"""
    @abc.abstractmethod
    def output(self, result: DeploymentTestResult) -> TestDeploymentInferenceOutput:
        pass


# ======================================
# Usecaseの具体的な実装 (Interactor)
# ======================================
class TestDeploymentInferenceInteractor:
    def __init__(
        self,
        presenter: "TestDeploymentInferencePresenter",
        deployment_repo: DeploymentRepository,
        job_repo: FinetuningJobRepository,
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
        test_service: DeploymentTestDomainService
    ):
        self.presenter = presenter
        self.deployment_repo = deployment_repo
        self.job_repo = job_repo
        self.agent_repo = agent_repo
        self.auth_service = auth_service
        self.test_service = test_service

    # 修正: execute メソッドを非同期 (async) に変更
    async def execute(
        self, input: TestDeploymentInferenceInput
    ) -> Tuple["TestDeploymentInferenceOutput", Exception | None]:
        
        try:
            # 1. 認証 (Auth)
            user: User = self.auth_service.verify_token(input.token)
            
            # 2. デプロイメントの取得
            deployment_id_vo = ID(input.deployment_id)
            deployment: Optional[Deployment] = self.deployment_repo.find_by_id(deployment_id_vo)
            
            if deployment is None or deployment.endpoint is None:
                raise FileNotFoundError("Deployment not found or endpoint is not active.")

            # 3. Job ID と Agent ID を辿り、権限チェック
            job_id_vo = deployment.job_id
            job: Optional[FinetuningJob] = self.job_repo.find_by_id(job_id_vo)
            
            if job is None:
                raise FileNotFoundError(f"Job {job_id_vo.value} not found (Deployment linked to non-existent job).")

            agent: Optional[Agent] = self.agent_repo.find_by_id(job.agent_id)
            if agent is None or agent.user_id != user.id:
                raise PermissionError("User does not have permission to run tests for this deployment.")

            # 4. ロジック本体: テストサービスを使って推論テストを実行
            # 修正: asyncio.run_until_complete を削除し、直接 await
            test_result_vo: DeploymentTestResult = await self.test_service.run_batch_inference_test(
                test_file=input.test_file,
                endpoint_url=deployment.endpoint
            )

            # 5. Presenterに渡してOutput DTOに変換
            output = self.presenter.output(test_result_vo)
            return output, None
            
        except Exception as e:
            # エラー時は空のOutput DTOと例外を返す
            empty_output = TestDeploymentInferenceOutput(
                test_result=TestMetricsOutput(overall_metrics={}, case_results=[]),
                message="Test failed."
            )
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_test_deployment_inference_interactor(
    presenter: "TestDeploymentInferencePresenter",
    deployment_repo: DeploymentRepository,
    job_repo: FinetuningJobRepository,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
    test_service: DeploymentTestDomainService
) -> "TestDeploymentInferenceUseCase":
    return TestDeploymentInferenceInteractor(
        presenter=presenter,
        deployment_repo=deployment_repo,
        job_repo=job_repo,
        agent_repo=agent_repo,
        auth_service=auth_service,
        test_service=test_service
    )