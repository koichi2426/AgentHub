import json
from typing import Dict, Optional

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

# --- Controller / Presenter / Usecase imports ---
# (Signup)
from adapter.controller.auth_signup_controller import CreateUserController
from adapter.presenter.auth_signup_presenter import new_auth_signup_presenter
from usecase.auth_signup import CreateUserInput, new_create_user_interactor

# (Login)
from adapter.controller.auth_login_controller import LoginUserController
from adapter.presenter.auth_login_presenter import new_login_user_presenter
from usecase.auth_login import LoginUserInput, new_login_user_interactor

# (Get User)
from adapter.controller.get_user_controller import GetUserController
from adapter.presenter.get_user_presenter import new_get_user_presenter
from usecase.get_user import GetUserInput, new_get_user_interactor

# (Infrastructure / Domain Services)
from infrastructure.database.mysql.user_repository import MySQLUserRepository
from infrastructure.database.mysql.config import NewMySQLConfigFromEnv
from infrastructure.domain.services.auth_domain_service_impl import NewAuthDomainService


# === Router Setup ===
router = APIRouter()
db_config = NewMySQLConfigFromEnv()
user_repo = MySQLUserRepository(db_config)
ctx_timeout = 10.0
oauth2_scheme = HTTPBearer()


# --- Helper: 共通レスポンス処理 ---
def handle_response(response_dict: Dict, success_code: int = 200):
    status_code = response_dict.get("status", 500)
    data = response_dict.get("data")

    if status_code >= 400:
        if hasattr(data, 'dict'):
             data = data.dict()
        return JSONResponse(content=data, status_code=status_code)

    if success_code == 204:
        return Response(status_code=204)

    try:
        if hasattr(data, 'dict'):
            data = data.dict()
        content_str = json.dumps(data, default=str)
        content_data = json.loads(content_str)
    except TypeError:
        content_data = {"error": "Failed to serialize response data"}
        status_code = 500

    return JSONResponse(content=content_data, status_code=success_code if status_code < 400 else status_code)


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


# === Auth Routes ===
@router.post("/v1/auth/signup")
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


@router.post("/v1/auth/login")
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


# ▼▼▼ [追加] ユーザー情報取得エンドポイント ▼▼▼
@router.get("/v1/users/me")
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
# ▲▲▲ 追加ここまで ▲▲▲

