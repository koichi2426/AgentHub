import json
from typing import Dict, Optional, List
from dataclasses import is_dataclass, asdict

from fastapi import APIRouter, Depends, UploadFile, File
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


# (Infrastructure / Domain Services)
from infrastructure.database.mysql.user_repository import MySQLUserRepository
from infrastructure.database.mysql.agent_repository import MySQLAgentRepository 
# ▼▼▼ [新規追加] Finetuning Job Repository をインポート ▼▼▼
from infrastructure.database.mysql.finetuning_job_repository import MySQLFinetuningJobRepository
# ▲▲▲ 新規追加ここまで ▲▲▲
from infrastructure.database.mysql.config import NewMySQLConfigFromEnv
from infrastructure.domain.services.auth_domain_service_impl import NewAuthDomainService
# ▼▼▼ [新規追加] New Domain Service Impls をインポート ▼▼▼
from infrastructure.domain.services.file_storage_domain_service_impl import NewFileStorageDomainService
from infrastructure.domain.services.job_queue_domain_service_impl import NewJobQueueDomainService
# ▲▲▲ 新規追加ここまで ▲▲▲


# === Router Setup ===
router = APIRouter()
db_config = NewMySQLConfigFromEnv()
user_repo = MySQLUserRepository(db_config)
agent_repo = MySQLAgentRepository(db_config) 
# ▼▼▼ [新規追加] Finetuning Job Repository をインスタンス化 ▼▼▼
finetuning_job_repo = MySQLFinetuningJobRepository(db_config) 
# ▲▲▲ 新規追加ここまで ▲▲▲
ctx_timeout = 10.0
oauth2_scheme = HTTPBearer()

# ▼▼▼ [新規追加] 新しいドメインサービスをインスタンス化 ▼▼▼
file_storage_service = NewFileStorageDomainService()
job_queue_service = NewJobQueueDomainService()
# ▲▲▲ 新規追加ここまで ▲▲▲


# --- Helper: 共通レスポンス処理 ---
def handle_response(response_dict: Dict, success_code: int = 200):
    status_code = response_dict.get("status", 500)
    data = response_dict.get("data")

    if is_dataclass(data):
        data = asdict(data)

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


# === Auth and User Routes (中略) ===
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


# ▼▼▼ [新規追加] ファインチューニングジョブ作成エンドポイント ▼▼▼
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
        print("# 1. Adapterを使用してFastAPIのUploadFileをドメインの抽象型に変換")
        # 1. Adapterを使用してFastAPIのUploadFileをドメインの抽象型に変換
        domain_file_stream = FastAPIUploadedFileAdapter(training_file)

        print("# 2. Input DTO を構築")
        # 2. Input DTO を構築
        input_data = CreateFinetuningJobInput(
            token=token,
            agent_id=agent_id,
            training_file=domain_file_stream # 抽象化されたファイルストリームを渡す
        )

        print("# 3. 組み立て")
        # 3. 組み立て
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_create_finetuning_job_presenter()
        
        usecase = new_create_finetuning_job_interactor(
            presenter=presenter,
            job_repo=finetuning_job_repo,          
            agent_repo=agent_repo,
            auth_service=auth_service,
            file_storage_service=file_storage_service, 
            job_queue_service=job_queue_service,       
        )
        controller = CreateFinetuningJobController(usecase)

        print("# 4. Controllerを実行")
        # 4. Controllerを実行 (Input DTOを引数として渡す形式)
        response_dict = controller.execute(
            input_data=input_data 
        )
        
        # 5. 応答 (キューイングに成功したら 201 Created)
        return handle_response(response_dict, success_code=201)
    
    except Exception as e:
        return JSONResponse({"error": f"An unexpected error occurred: {e}"}, status_code=500)
# ▲▲▲ 新規追加ここまで ▲▲▲