import json
from typing import Dict, Union, Any, List, Optional
from dataclasses import is_dataclass, asdict
from datetime import datetime # JSON変換ロジックで使用

from fastapi import APIRouter, Depends, UploadFile, File, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

# --- Controller / Presenter / Usecase imports ---
# (Signup)
from adapter.controller.auth_signup_controller import CreateUserController
from adapter.presenter.auth_signup_presenter import new_auth_signup_presenter
from usecase.auth_signup import CreateUserInput, CreateUserOutput, new_create_user_interactor

# (Login)
from adapter.controller.auth_login_controller import LoginUserController
from adapter.presenter.auth_login_presenter import new_login_user_presenter
from usecase.auth_login import LoginUserInput, LoginUserOutput, new_login_user_interactor

# (Get User)
from adapter.controller.get_user_controller import GetUserController
from adapter.presenter.get_user_presenter import new_get_user_presenter
from usecase.get_user import GetUserInput, GetUserOutput, new_get_user_interactor

# (Create Agent)
from adapter.controller.create_agent_controller import CreateAgentController
from adapter.presenter.create_agent_presenter import new_create_agent_presenter
from usecase.create_agent import CreateAgentInput, CreateAgentOutput, new_create_agent_interactor

# (Get User Agents)
from adapter.controller.get_user_agents_controller import GetUserAgentsController
from adapter.presenter.get_user_agents_presenter import new_get_user_agents_presenter
from usecase.get_user_agents import GetUserAgentsInput, GetUserAgentsOutput, new_get_user_agents_interactor

# ▼▼▼ [新規追加] Create Finetuning Job 関連のインポート ▼▼▼
from adapter.controller.create_finetuning_job_controller import CreateFinetuningJobController
from adapter.presenter.create_finetuning_job_presenter import new_create_finetuning_job_presenter
from usecase.create_finetuning_job import CreateFinetuningJobInput, CreateFinetuningJobOutput, new_create_finetuning_job_interactor
from infrastructure.domain.value_objects.file_data_impl import FastAPIUploadedFileAdapter # ファイルアダプタ
# ▲▲▲ 新規追加ここまで ▲▲▲

# ▼▼▼ [新規追加] Get Finetuning Jobs 関連のインポート ▼▼▼
from adapter.controller.get_user_finetuning_jobs_controller import GetUserFinetuningJobsController
from adapter.presenter.get_user_finetuning_jobs_presenter import new_get_user_finetuning_jobs_presenter
from usecase.get_user_finetuning_jobs import GetUserFinetuningJobsInput, GetUserFinetuningJobsOutput, new_get_user_finetuning_jobs_interactor
# ▲▲▲ 新規追加ここまで ▲▲▲

# ▼▼▼ [新規追加] Get Weight Visualizations 関連のインポート ★★★ ▼▼▼
from adapter.controller.get_weight_visualizations_controller import GetWeightVisualizationsController
from adapter.presenter.get_weight_visualizations_presenter import new_get_finetuning_job_visualization_presenter
from usecase.get_weight_visualizations import GetFinetuningJobVisualizationInput, GetFinetuningJobVisualizationOutput, new_get_finetuning_job_visualization_interactor
# ▲▲▲ 新規追加ここまで ★★★ ▼▼▼


# (Infrastructure / Domain Services)
from infrastructure.database.mysql.user_repository import MySQLUserRepository
from infrastructure.database.mysql.agent_repository import MySQLAgentRepository 
# ▼▼▼ [新規追加] Finetuning Job Repository をインポート ▼▼▼
from infrastructure.database.mysql.finetuning_job_repository import MySQLFinetuningJobRepository
# ▼▼▼ [新規追加] Weight Visualization Repository をインポート ★★★ ▼▼▼
from infrastructure.database.mysql.weight_visualization_repository import MySQLWeightVisualizationRepository
# ▲▲▲ 新規追加ここまで ★★★ ▲▲▲

from infrastructure.database.mysql.config import NewMySQLConfigFromEnv
from infrastructure.domain.services.auth_domain_service_impl import NewAuthDomainService
# ▼▼▼ [新規追加] New Domain Service Impls をインポート ▼▼▼
from infrastructure.domain.services.file_storage_domain_service_impl import NewFileStorageDomainService
from infrastructure.domain.services.job_queue_domain_service_impl import NewJobQueueDomainService
from infrastructure.domain.services.system_time_domain_service_impl import NewSystemTimeDomainService 
# ▲▲▲ 新規追加ここまで ▼▼▼


# === Router Setup ===
router = APIRouter()
db_config = NewMySQLConfigFromEnv()
user_repo = MySQLUserRepository(db_config)
agent_repo = MySQLAgentRepository(db_config) 
# ▼▼▼ [新規追加] Finetuning Job Repository をインスタンス化 ▼▼▼
finetuning_job_repo = MySQLFinetuningJobRepository(db_config) 
# ▼▼▼ [新規追加] Weight Visualization Repository をインスタンス化 ★★★ ▼▼▼
weight_visualization_repo = MySQLWeightVisualizationRepository(db_config)
# ▲▲▲ 新規追加ここまで ★★★ ▲▲▲

ctx_timeout = 10.0
oauth2_scheme = HTTPBearer()

# ▼▼▼ [新規追加] 新しいドメインサービスをインスタンス化 ▼▼▼
file_storage_service = NewFileStorageDomainService()
job_queue_service = NewJobQueueDomainService()
system_time_service = NewSystemTimeDomainService() 
# ▲▲▲ 新規追加ここまで ▲▲▲


# --- Helper: 共通レスポンス処理 ---
def handle_response(response_dict: Dict, success_code: int = 200):
    status_code = response_dict.get("status", 500)
    data = response_dict.get("data")

    # DTOを辞書に変換
    if is_dataclass(data):
        data = asdict(data)
        
        # 修正: datetimeオブジェクトをISO文字列に変換
        def convert_datetime_to_str(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, dict):
                return {k: convert_datetime_to_str(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_datetime_to_str(v) for v in obj]
            return obj
        
        data = convert_datetime_to_str(data)
        # 修正ここまで

    if status_code >= 400:
        return JSONResponse(content=data, status_code=status_code)

    if success_code == 204:
        return Response(status_code=204)

    return JSONResponse(content=data, status_code=success_code)


# === Request DTOs ===
class CreateUserRequest(BaseModel):
    username: str
    name: str
    email: str
    avatar_url: str
    password: str

class LoginUserRequest(BaseModel):
    email: str
    password: str

class CreateAgentRequest(BaseModel):
    name: str
    description: Optional[str]


# === Auth and User Routes ===
@router.post("/v1/auth/signup", response_model=CreateUserOutput)
def create_user(request: CreateUserRequest):
    try:
        # 組み立て
        repo = user_repo 
        presenter = new_auth_signup_presenter()
        usecase = new_create_user_interactor(presenter, repo, ctx_timeout)
        controller = CreateUserController(usecase)

        # DTO 作成して実行
        input_data = CreateUserInput(**request.dict())
        response_dict = controller.execute(input_data)
        return handle_response(response_dict, success_code=201)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/v1/auth/login", response_model=LoginUserOutput)
def login_user(request: LoginUserRequest):
    try:
        # 組み立て
        repo = user_repo 
        auth_service = NewAuthDomainService(repo)
        presenter = new_login_user_presenter()
        usecase = new_login_user_interactor(presenter, auth_service, ctx_timeout)
        controller = LoginUserController(usecase)

        # DTO 作成して実行
        input_data = LoginUserInput(**request.dict())
        response_dict = controller.execute(input_data)
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/v1/users/me", response_model=GetUserOutput)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        token = credentials.credentials

        # 組み立て
        repo = user_repo
        auth_service = NewAuthDomainService(repo)
        presenter = new_get_user_presenter()
        usecase = new_get_user_interactor(presenter, auth_service, ctx_timeout)
        controller = GetUserController(usecase)

        # DTOを作成して実行
        input_data = GetUserInput(token=token)
        response_dict = controller.execute(input_data)
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# エージェント作成エンドポイント
@router.post("/v1/agents", response_model=CreateAgentOutput)
def create_agent(
    request: CreateAgentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        
        # 組み立て
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_create_agent_presenter()
        usecase = new_create_agent_interactor(presenter, agent_repo, auth_service, ctx_timeout)
        controller = CreateAgentController(usecase)

        # DTOを作成して実行
        input_data = CreateAgentInput(
            token=token,
            name=request.name,
            description=request.description
        )
        response_dict = controller.execute(input_data)
        return handle_response(response_dict, success_code=201)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ユーザーのエージェント一覧取得エンドポイント
@router.get("/v1/agents", response_model=GetUserAgentsOutput)
def get_user_agents(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    認証されたユーザーが作成した全てのエージェント一覧を取得するAPIエンドポイント。
    """
    try:
        token = credentials.credentials
        
        # 組み立て
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_get_user_agents_presenter()
        usecase = new_get_user_agents_interactor(presenter, agent_repo, auth_service)
        controller = GetUserAgentsController(usecase)

        # DTOを作成して実行
        response_dict = controller.execute(token=token) 
        
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ▼▼▼ ファインチューニングジョブ作成エンドポイント ▼▼▼
@router.post("/v1/agents/{agent_id}/finetuning", response_model=CreateFinetuningJobOutput)
def create_finetuning_job(
    agent_id: int,
    training_file: UploadFile = File(..., description="Training data file (.txt)"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """
    トレーニングデータファイルを受け付け、ファインチューニングジョブをキューに投入する。
    """
    try:
        token = credentials.credentials
        
        # 1. Adapterを使用してFastAPIのUploadFileをドメインの抽象型に変換
        domain_file_stream = FastAPIUploadedFileAdapter(training_file)

        # 2. Input DTO を構築
        input_data = CreateFinetuningJobInput(
            token=token,
            agent_id=agent_id,
            training_file=domain_file_stream # 抽象化されたファイルストリームを渡す
        )

        # 3. 組み立て
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_create_finetuning_job_presenter()
        
        # NewFinetuningJobInteractorにサービスをDI
        usecase = new_create_finetuning_job_interactor(
            presenter=presenter,
            job_repo=finetuning_job_repo,          
            agent_repo=agent_repo,
            auth_service=auth_service,
            file_storage_service=file_storage_service, 
            job_queue_service=job_queue_service,       
            system_time_service=system_time_service, 
        )
        controller = CreateFinetuningJobController(usecase)

        # 4. Controllerを実行 (Input DTOを引数として渡す形式)
        response_dict = controller.execute(
            input_data=input_data 
        )
        
        # 5. 応答 (キューイングに成功したら 201 Created)
        return handle_response(response_dict, success_code=201)
    
    except Exception as e:
        return JSONResponse({"error": f"An unexpected error occurred: {e}"}, status_code=500)
# ▲▲▲ ファインチューニングジョブ作成エンドポイント ▲▲▲


# ▼▼▼ ユーザーのファインチューニングジョブ一覧取得エンドポイント ▼▼▼
@router.get("/v1/jobs", response_model=GetUserFinetuningJobsOutput)
def get_user_finetuning_jobs(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    認証されたユーザーが所有する全てのエージェントのファインチューニングジョブ一覧を取得する。
    """
    try:
        token = credentials.credentials
        
        # 組み立て
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_get_user_finetuning_jobs_presenter()
        
        usecase = new_get_user_finetuning_jobs_interactor(
            presenter=presenter,
            job_repo=finetuning_job_repo,
            auth_service=auth_service,
        )
        controller = GetUserFinetuningJobsController(usecase)

        # Controllerを実行 (Input DTOを構築せずに直接トークンを渡す形式)
        response_dict = controller.execute(token=token)
        
        return handle_response(response_dict, success_code=200)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
# ▲▲▲ ユーザーのファインチューニングジョブ一覧取得エンドポイント ▲▲▲


# ▼▼▼ [新規追加] 重み可視化データ取得エンドポイント ★★★ ▼▼▼
@router.get("/v1/jobs/{job_id}/visualizations", response_model=GetFinetuningJobVisualizationOutput)
def get_job_visualizations(
    job_id: int = Path(..., description="ID of the Finetuning Job"), 
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """
    特定のファインチューニングジョブIDに紐づく重み変化の可視化データ (ヒートマップURLなど) を取得する。
    """
    try:
        token = credentials.credentials
        
        # 1. Input DTOの生成
        input_data = GetFinetuningJobVisualizationInput(token=token, job_id=job_id)
        
        # 2. 組み立て
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_get_finetuning_job_visualization_presenter()
        
        usecase = new_get_finetuning_job_visualization_interactor(
            presenter=presenter,
            vis_repo=weight_visualization_repo,
            job_repo=finetuning_job_repo,
            agent_repo=agent_repo,
            auth_service=auth_service,
        )
        controller = GetWeightVisualizationsController(usecase)

        # 3. Controllerを実行
        response_dict = controller.execute(
            token=token,
            job_id=job_id,
        )
        
        # 4. 応答
        return handle_response(response_dict, success_code=200)
    
    except Exception as e:
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)
# ▲▲▲ 新規追加ここまで ★★★ ▼▼▼