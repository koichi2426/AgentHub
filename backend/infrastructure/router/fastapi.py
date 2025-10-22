import json
from typing import Dict, Optional, List # Listをインポート
from dataclasses import is_dataclass, asdict # dataclassを扱うためにインポート

from fastapi import APIRouter, Depends
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

# ▼▼▼ [追記] Get User Agents 関連のインポート ▼▼▼
from adapter.controller.get_user_agents_controller import GetUserAgentsController
from adapter.presenter.get_user_agents_presenter import new_get_user_agents_presenter
from usecase.get_user_agents import GetUserAgentsInput, GetUserAgentsOutput, new_get_user_agents_interactor
# ▲▲▲ 追記ここまで ▲▲▲

# (Infrastructure / Domain Services)
from infrastructure.database.mysql.user_repository import MySQLUserRepository
from infrastructure.database.mysql.agent_repository import MySQLAgentRepository # Agentリポジトリをインポート
from infrastructure.database.mysql.config import NewMySQLConfigFromEnv
from infrastructure.domain.services.auth_domain_service_impl import NewAuthDomainService


# === Router Setup ===
router = APIRouter()
db_config = NewMySQLConfigFromEnv()
user_repo = MySQLUserRepository(db_config)
agent_repo = MySQLAgentRepository(db_config) # Agentリポジトリをインスタンス化
ctx_timeout = 10.0
oauth2_scheme = HTTPBearer()


# --- Helper: 共通レスポンス処理 ---
def handle_response(response_dict: Dict, success_code: int = 200):
    status_code = response_dict.get("status", 500)
    data = response_dict.get("data")

    # ▼▼▼ [修正] DTO(dataclass)を辞書に変換する処理を追加 ▼▼▼
    if is_dataclass(data):
        data = asdict(data)
    # ▲▲▲ 修正ここまで ▲▲▲

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


# ▼▼▼ [新規追加] ユーザーのエージェント一覧取得エンドポイント ▼▼▼
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
        # GetUserAgentsInteractor は timeout_sec を受け取らないため、引数から除外
        usecase = new_get_user_agents_interactor(presenter, agent_repo, auth_service)
        controller = GetUserAgentsController(usecase)

        # DTOを作成して実行
        # Controllerは token を直接受け取るため、Input DTOの生成は省略し直接実行
        response_dict = controller.execute(token=token) 
        
        # GETリクエストの成功コードは 200 OK
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
# ▲▲▲ 新規追加ここまで ▲▲▲