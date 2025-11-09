import json
from typing import Dict, Union, Any, List, Optional
from dataclasses import is_dataclass, asdict
from datetime import datetime 
from io import BytesIO 

from fastapi import APIRouter, Depends, UploadFile, File, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel
import httpx

# --- Controller / Presenter / Usecase imports ---
from adapter.controller.auth_signup_controller import CreateUserController
from adapter.presenter.auth_signup_presenter import new_auth_signup_presenter
from usecase.auth_signup import CreateUserInput, CreateUserOutput, new_create_user_interactor

from adapter.controller.auth_login_controller import LoginUserController
from adapter.presenter.auth_login_presenter import new_login_user_presenter
from usecase.auth_login import LoginUserInput, LoginUserOutput, new_login_user_interactor

from adapter.controller.get_user_controller import GetUserController
from adapter.presenter.get_user_presenter import new_get_user_presenter
from usecase.get_user import GetUserInput, GetUserOutput, new_get_user_interactor

from adapter.controller.create_agent_controller import CreateAgentController
from adapter.presenter.create_agent_presenter import new_create_agent_presenter
from usecase.create_agent import CreateAgentInput, CreateAgentOutput, new_create_agent_interactor

from adapter.controller.get_user_agents_controller import GetUserAgentsController
from adapter.presenter.get_user_agents_presenter import new_get_user_agents_presenter
from usecase.get_user_agents import GetUserAgentsInput, GetUserAgentsOutput, new_get_user_agents_interactor

from adapter.controller.get_agents_controller import GetAgentsController
from adapter.presenter.get_agents_presenter import new_get_agents_presenter
from usecase.get_agents import GetAgentsInput, GetAgentsOutput, new_get_agents_interactor

from adapter.controller.create_finetuning_job_controller import CreateFinetuningJobController
from adapter.presenter.create_finetuning_job_presenter import new_create_finetuning_job_presenter
from usecase.create_finetuning_job import CreateFinetuningJobInput, CreateFinetuningJobOutput, new_create_finetuning_job_interactor
from infrastructure.domain.value_objects.file_data_impl import FastAPIUploadedFileAdapter

from adapter.controller.get_agent_finetuning_jobs_controller import GetAgentFinetuningJobsController
from adapter.presenter.get_agent_finetuning_jobs_presenter import new_get_agent_finetuning_jobs_presenter
from usecase.get_agent_finetuning_jobs import GetAgentFinetuningJobsInput, GetAgentFinetuningJobsOutput, new_get_agent_finetuning_jobs_interactor

from adapter.controller.get_agent_deployments_controller import GetAgentDeploymentsController
from adapter.presenter.get_agent_deployments_presenter import new_get_agent_deployments_presenter
from usecase.get_agent_deployments import GetAgentDeploymentsInput, GetAgentDeploymentsOutput, new_get_agent_deployments_interactor

from adapter.controller.get_weight_visualizations_controller import GetWeightVisualizationsController
from adapter.presenter.get_weight_visualizations_presenter import new_get_finetuning_job_visualization_presenter
from usecase.get_weight_visualizations import GetFinetuningJobVisualizationInput, GetFinetuningJobVisualizationOutput, new_get_finetuning_job_visualization_interactor

from adapter.controller.get_image_stream_controller import GetImageStreamController
from adapter.presenter.get_image_stream_presenter import new_get_image_stream_presenter
from usecase.get_image_stream import GetImageStreamInput, GetImageStreamOutput, new_get_image_stream_interactor

from adapter.controller.test_deployment_inference_controller import TestDeploymentInferenceController
from adapter.presenter.test_deployment_inference_presenter import new_test_deployment_inference_presenter
from usecase.test_deployment_inference import TestDeploymentInferenceInput, TestDeploymentInferenceOutput, new_test_deployment_inference_interactor
from infrastructure.domain.services.deployment_test_domain_service_impl import DeploymentTestDomainServiceImpl

# (Infrastructure / Domain Services)
from infrastructure.database.mysql.user_repository import MySQLUserRepository
from infrastructure.database.mysql.agent_repository import MySQLAgentRepository 
from infrastructure.database.mysql.finetuning_job_repository import MySQLFinetuningJobRepository
from infrastructure.database.mysql.weight_visualization_repository import MySQLWeightVisualizationRepository
from infrastructure.database.mysql.config import NewMySQLConfigFromEnv
from infrastructure.domain.services.auth_domain_service_impl import NewAuthDomainService
from infrastructure.domain.services.file_storage_domain_service_impl import NewFileStorageDomainService
from infrastructure.domain.services.job_queue_domain_service_impl import NewJobQueueDomainService
from infrastructure.domain.services.system_time_domain_service_impl import NewSystemTimeDomainService 
from infrastructure.domain.services.get_image_stream_domain_service_impl import NewFileStreamDomainService

# (4 NEW DEPLOYMENT APIs IMPORTS)
from infrastructure.database.mysql.deployment_repository import MySQLDeploymentRepository
from infrastructure.database.mysql.methods_repository import MySQLMethodsRepository
from infrastructure.domain.services.job_method_finder_domain_service_impl import JobMethodFinderDomainServiceImpl

from adapter.controller.create_finetuning_job_deployment_controller import CreateFinetuningJobDeploymentController
from adapter.presenter.create_finetuning_job_deployment_presenter import new_create_finetuning_job_deployment_presenter
from usecase.create_finetuning_job_deployment import CreateFinetuningJobDeploymentInput, CreateFinetuningJobDeploymentOutput, new_create_finetuning_job_deployment_interactor

from adapter.controller.get_finetuning_job_deployment_controller import GetFinetuningJobDeploymentController
from adapter.presenter.get_finetuning_job_deployment_presenter import new_get_finetuning_job_deployment_presenter
from usecase.get_finetuning_job_deployment import GetFinetuningJobDeploymentInput, GetFinetuningJobDeploymentOutput, new_get_finetuning_job_deployment_interactor

from adapter.controller.get_deployment_methods_controller import GetDeploymentMethodsController
from adapter.presenter.get_deployment_methods_presenter import new_get_deployment_methods_presenter
from usecase.get_deployment_methods import GetDeploymentMethodsInput, GetDeploymentMethodsOutput, new_get_deployment_methods_interactor

from adapter.controller.set_deployment_methods_controller import SetDeploymentMethodsController
from adapter.presenter.set_deployment_methods_presenter import new_set_deployment_methods_presenter
from usecase.set_deployment_methods import SetDeploymentMethodsInput, SetDeploymentMethodsOutput, new_set_deployment_methods_interactor


# === Router Setup ===
router = APIRouter()
db_config = NewMySQLConfigFromEnv()
user_repo = MySQLUserRepository(db_config)
agent_repo = MySQLAgentRepository(db_config) 
finetuning_job_repo = MySQLFinetuningJobRepository(db_config) 
weight_visualization_repo = MySQLWeightVisualizationRepository(db_config)
ctx_timeout = 10.0
oauth2_scheme = HTTPBearer()

file_storage_service = NewFileStorageDomainService()
job_queue_service = NewJobQueueDomainService()
system_time_service = NewSystemTimeDomainService() 
file_stream_service = NewFileStreamDomainService() 

# DI Setup
deployment_repo = MySQLDeploymentRepository(db_config)
methods_repo = MySQLMethodsRepository(db_config)
job_method_finder_service = JobMethodFinderDomainServiceImpl(timeout=5)
auth_service = NewAuthDomainService(user_repo) 

async_http_client = httpx.AsyncClient(timeout=15.0) 
test_inference_service = DeploymentTestDomainServiceImpl(client=async_http_client)


# --- Helper: 共通レスポンス処理 ---
def handle_response(response_dict: Dict, success_code: int = 200):
    status_code = response_dict.get("status", 500)
    data = response_dict.get("data")

    if isinstance(data, StreamingResponse):
        return data
        
    if is_dataclass(data):
        data = asdict(data)
        
        def convert_datetime_to_str(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, dict):
                return {k: convert_datetime_to_str(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_datetime_to_str(v) for v in obj]
            return obj
        
        data = convert_datetime_to_str(data)

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
        repo = user_repo 
        presenter = new_auth_signup_presenter()
        usecase = new_create_user_interactor(presenter, repo, ctx_timeout)
        controller = CreateUserController(usecase)
        input_data = CreateUserInput(**request.dict())
        response_dict = controller.execute(input_data)
        return handle_response(response_dict, success_code=201)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/v1/auth/login", response_model=LoginUserOutput)
def login_user(request: LoginUserRequest):
    try:
        repo = user_repo 
        auth_service = NewAuthDomainService(repo)
        presenter = new_login_user_presenter()
        usecase = new_login_user_interactor(presenter, auth_service, ctx_timeout)
        controller = LoginUserController(usecase)
        input_data = LoginUserInput(**request.dict())
        response_dict = controller.execute(input_data)
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/v1/users/me", response_model=GetUserOutput)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        token = credentials.credentials
        repo = user_repo
        auth_service = NewAuthDomainService(repo)
        presenter = new_get_user_presenter()
        usecase = new_get_user_interactor(presenter, auth_service, ctx_timeout)
        controller = GetUserController(usecase)
        input_data = GetUserInput(token=token)
        response_dict = controller.execute(input_data)
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# === Agent Routes ===
@router.post("/v1/agents", response_model=CreateAgentOutput)
def create_agent(
    request: CreateAgentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_create_agent_presenter()
        usecase = new_create_agent_interactor(presenter, agent_repo, auth_service, ctx_timeout)
        controller = CreateAgentController(usecase)
        input_data = CreateAgentInput(
            token=token,
            name=request.name,
            description=request.description
        )
        response_dict = controller.execute(input_data)
        return handle_response(response_dict, success_code=201)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/v1/agents", response_model=GetUserAgentsOutput)
def get_user_agents(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    認証されたユーザーが作成した全てのエージェント一覧を取得するAPIエンドポイント。
    """
    try:
        token = credentials.credentials
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_get_user_agents_presenter()
        usecase = new_get_user_agents_interactor(presenter, agent_repo, auth_service)
        controller = GetUserAgentsController(usecase)
        response_dict = controller.execute(token=token) 
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/v1/agents/all", response_model=GetAgentsOutput)
def get_all_agents():
    try:
        presenter = new_get_agents_presenter()
        usecase = new_get_agents_interactor(presenter, agent_repo)
        controller = GetAgentsController(usecase)
        # Input DTOを渡す際は、キーワード引数 'input_data' を使用する
        response_dict = controller.execute(input_data=GetAgentsInput()) 
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)


# === Finetuning & Job Routes ===
@router.post("/v1/agents/{agent_id}/finetuning", response_model=CreateFinetuningJobOutput)
def create_finetuning_job(
    agent_id: int,
    training_file: UploadFile = File(..., description="Training data file (.txt)"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        domain_file_stream = FastAPIUploadedFileAdapter(training_file)
        input_data = CreateFinetuningJobInput(
            token=token,
            agent_id=agent_id,
            training_file=domain_file_stream
        )
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_create_finetuning_job_presenter()
        usecase = new_create_finetuning_job_interactor(
            presenter=presenter, job_repo=finetuning_job_repo, agent_repo=agent_repo,
            auth_service=auth_service, file_storage_service=file_storage_service, 
            job_queue_service=job_queue_service, system_time_service=system_time_service, 
        )
        controller = CreateFinetuningJobController(usecase)
        response_dict = controller.execute(input_data=input_data)
        return handle_response(response_dict, success_code=201)
    except Exception as e:
        return JSONResponse({"error": f"An unexpected error occurred: {e}"}, status_code=500)


@router.get("/v1/agents/{agent_id}/jobs", response_model=GetAgentFinetuningJobsOutput)
def get_agent_finetuning_jobs(
    agent_id: int = Path(..., description="ID of the Agent"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        auth_service = NewAuthDomainService(user_repo)
        
        presenter = new_get_agent_finetuning_jobs_presenter() 
        usecase = new_get_agent_finetuning_jobs_interactor(
            presenter=presenter, 
            job_repo=finetuning_job_repo, 
            auth_service=auth_service,
            agent_repo=agent_repo, 
        )

        controller = GetAgentFinetuningJobsController(usecase) 
        response_dict = controller.execute(token=token, agent_id=agent_id) 
        
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/v1/jobs/{job_id}/visualizations", response_model=GetFinetuningJobVisualizationOutput)
def get_job_visualizations(
    job_id: int = Path(..., description="ID of the Finetuning Job"), 
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        input_data = GetFinetuningJobVisualizationInput(token=token, job_id=job_id)
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_get_finetuning_job_visualization_presenter()
        usecase = new_get_finetuning_job_visualization_interactor(
            presenter=presenter, vis_repo=weight_visualization_repo, job_repo=finetuning_job_repo,
            agent_repo=agent_repo, auth_service=auth_service,
        )
        controller = GetWeightVisualizationsController(usecase)
        response_dict = controller.execute(token=token, job_id=job_id)
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)


# === Deployment Routes ===
@router.get("/v1/agents/{agent_id}/deployments", response_model=GetAgentDeploymentsOutput)
def get_agent_deployments(
    agent_id: int = Path(..., description="ID of the Agent"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        auth_service = NewAuthDomainService(user_repo)

        presenter = new_get_agent_deployments_presenter()
        usecase = new_get_agent_deployments_interactor(
            presenter=presenter,
            deployment_repo=deployment_repo,
            agent_repo=agent_repo,
            auth_service=auth_service,
        )

        controller = GetAgentDeploymentsController(usecase)
        response_dict = controller.execute(token=token, agent_id=agent_id)
        
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/v1/jobs/{job_id}/deployment", response_model=CreateFinetuningJobDeploymentOutput)
def create_deployment(
    job_id: int = Path(..., description="ID of the Finetuning Job to deploy"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        input_data = CreateFinetuningJobDeploymentInput(token=token, job_id=job_id)
        
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_create_finetuning_job_deployment_presenter()
        
        usecase = new_create_finetuning_job_deployment_interactor(
            presenter=presenter,
            deployment_repo=deployment_repo,
            job_repo=finetuning_job_repo,
            agent_repo=agent_repo,
            auth_service=auth_service
        )
        controller = CreateFinetuningJobDeploymentController(usecase)
        response_dict = controller.execute(input_data=input_data)
        return handle_response(response_dict, success_code=201)
    except Exception as e:
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)


@router.get("/v1/jobs/{job_id}/deployment", response_model=GetFinetuningJobDeploymentOutput)
def get_deployment(
    job_id: int = Path(..., description="ID of the Finetuning Job"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        input_data = GetFinetuningJobDeploymentInput(token=token, job_id=job_id)
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_get_finetuning_job_deployment_presenter()
        
        usecase = new_get_finetuning_job_deployment_interactor(
            presenter=presenter,
            deployment_repo=deployment_repo,
            job_repo=finetuning_job_repo,
            agent_repo=agent_repo,
            auth_service=auth_service
        )
        controller = GetFinetuningJobDeploymentController(usecase)
        response_dict = controller.execute(input_data=input_data)
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)


@router.get("/v1/jobs/{job_id}/methods", response_model=GetDeploymentMethodsOutput)
def get_methods(
    job_id: int = Path(..., description="ID of the Finetuning Job"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        input_data = GetDeploymentMethodsInput(token=token, job_id=job_id)
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_get_deployment_methods_presenter()
        
        usecase = new_get_deployment_methods_interactor(
            presenter=presenter,
            methods_repo=methods_repo,
            deployment_repo=deployment_repo,
            job_repo=finetuning_job_repo,
            agent_repo=agent_repo,
            auth_service=auth_service
        )
        
        controller = GetDeploymentMethodsController(usecase)
        response_dict = controller.execute(input_data=input_data)
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)

@router.put("/v1/jobs/{job_id}/methods", response_model=SetDeploymentMethodsOutput) 
def set_methods(
    job_id: int = Path(..., description="ID of the Finetuning Job"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        
        input_data = SetDeploymentMethodsInput(
            token=token,
            job_id=job_id
        )
        
        auth_service = NewAuthDomainService(user_repo)
        presenter = new_set_deployment_methods_presenter()
        
        usecase = new_set_deployment_methods_interactor(
            presenter=presenter,
            methods_repo=methods_repo,
            deployment_repo=deployment_repo,
            job_repo=finetuning_job_repo,
            agent_repo=agent_repo,
            auth_service=auth_service,
            method_finder_service=job_method_finder_service 
        )
        
        controller = SetDeploymentMethodsController(usecase)
        response_dict = controller.execute(input_data=input_data)
        return handle_response(response_dict, success_code=200)
    except Exception as e:
        print(f"Set Methods Error: {e}") 
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)


@router.post("/v1/deployments/{deployment_id}/test", response_model=TestDeploymentInferenceOutput)
async def test_deployment_inference(
    deployment_id: int = Path(..., description="ID of the Deployment to test"),
    test_file: UploadFile = File(..., description="Test data file (.txt)"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    try:
        token = credentials.credentials
        
        domain_file_stream = FastAPIUploadedFileAdapter(test_file)
        
        input_data = TestDeploymentInferenceInput(
            token=token,
            deployment_id=deployment_id,
            test_file=domain_file_stream
        )
        
        presenter = new_test_deployment_inference_presenter()
        usecase = new_test_deployment_inference_interactor(
            presenter=presenter,
            deployment_repo=deployment_repo,
            job_repo=finetuning_job_repo,
            agent_repo=agent_repo,
            auth_service=auth_service,
            test_service=test_inference_service
        )
        
        controller = TestDeploymentInferenceController(usecase)
        
        response_dict = await controller.execute(input_data) 
        
        return handle_response(response_dict, success_code=200)
        
    except Exception as e:
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)


# === File Stream / Proxy Routes ===
@router.get("/v1/visuals/{filepath:path}", response_class=StreamingResponse)
async def serve_visualizations(filepath: str):
    try:
        presenter = new_get_image_stream_presenter()
        usecase = new_get_image_stream_interactor(
            presenter=presenter,
            file_stream_service=file_stream_service,
        )
        controller = GetImageStreamController(usecase)

        return controller.execute(relative_path=filepath)
    except Exception as e:
        return JSONResponse({"error": f"An unexpected server error occurred: {e}"}, status_code=500)