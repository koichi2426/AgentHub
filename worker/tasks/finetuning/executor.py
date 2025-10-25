# AGENTHUB/worker/tasks/finetuning/executor.py

import time
import os
import subprocess
import glob
import shutil
import json
import stat
import re
from datetime import datetime as PythonDateTime
from typing import Optional, List, Dict, Any, Tuple, BinaryIO
from contextlib import contextmanager

# === SFTP Client Implementation (Integrated but Refined) ===
import paramiko

class FileStorageError(Exception):
    """ファイルストレージ操作に関するカスタムエラー"""
    pass

class SFTPFileStorageService:
    """Paramiko (SFTP) を使用して、リモートVPSとのファイル操作を行うサービス。"""
    def __init__(self, vps_ip: str, vps_user: str, vps_account_password: str,
                 key_file_path: str, remote_training_dir: str,
                 remote_model_dir: str, vps_port: int = 22):
        self.vps_ip = vps_ip; self.vps_user = vps_user; self.vps_account_password = vps_account_password
        self.vps_port = vps_port; self.key_file_path = key_file_path
        self.remote_training_base_dir = remote_training_dir
        self.remote_model_base_dir = remote_model_dir
        self.remote_visuals_base_dir = f"/home/{self.vps_user}/visualizations"
        if not os.path.exists(self.key_file_path): raise FileNotFoundError(f"Key not found: {self.key_file_path}")
        try: self.private_key = paramiko.RSAKey(filename=self.key_file_path)
        except Exception as e: raise FileStorageError(f"Failed load key: {e}")
        print(f"INFO: SFTP Service init for {self.vps_user}@{self.vps_ip}")

    # contextmanager で接続を管理
    @contextmanager
    def connect(self) -> paramiko.SFTPClient:
        client = None
        sftp = None
        try:
            client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print(f"INFO: Connecting SFTP...")
            client.connect( self.vps_ip, port=self.vps_port, username=self.vps_user,
                            password=self.vps_account_password, pkey=self.private_key )
            sftp = client.open_sftp(); print(f"INFO: SFTP connected.")
            yield sftp
        except Exception as e:
            print(f"ERROR: SFTP connect/op failed: {e}"); raise FileStorageError(f"SFTP op failed: {e}")
        finally:
            if sftp:
                 try: sftp.close()
                 except Exception as e_close: print(f"WARN: SFTP close error: {e_close}")
            if client:
                 try: client.close()
                 except Exception as e_close: print(f"WARN: SSH client close error: {e_close}")
            print("INFO: SFTP Connection closed.")

    def _ensure_remote_dir_internal(self, sftp: paramiko.SFTPClient, remote_dir: str):
        # 以前の _ensure_remote_dir の実装 (簡略化のためインライン化も検討可)
        current_dir = ""
        if not remote_dir.startswith('/'): raise ValueError("Remote path must be absolute")
        parts = remote_dir.strip('/').split('/')
        if remote_dir.startswith('/'): parts.insert(0,'')
        for part in parts:
            if not part and current_dir != "": continue
            current_dir = "/" if current_dir == "" and part == "" else (current_dir + "/" + part).replace('//','/')
            if current_dir == "/": continue
            try: sftp_attrs = sftp.stat(current_dir)
            except FileNotFoundError:
                print(f"INFO: Creating remote directory: {current_dir}")
                try: sftp.mkdir(current_dir)
                except Exception as mkdir_e:
                     try: sftp.stat(current_dir) # Check again for race condition
                     except FileNotFoundError: raise FileStorageError(f"Failed create dir {current_dir}: {mkdir_e}")
            except Exception as e: raise FileStorageError(f"Error ensuring dir {current_dir}: {e}")

    def download_file(self, remote_path: str, local_path: str):
        with self.connect() as sftp:
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir): os.makedirs(local_dir, exist_ok=True)
            print(f"INFO: Downloading {remote_path} to {local_path}...")
            sftp.get(remote_path, local_path); print(f"INFO: Download successful.")

    def upload_directory(self, local_dir_path: str, remote_base_dir: str,
                         return_remote_paths: bool = False) -> Dict[str, str]:
        uploaded_paths = {}
        with self.connect() as sftp:
            self._ensure_remote_dir_internal(sftp, remote_base_dir)
            print(f"INFO: Uploading dir {local_dir_path} to {remote_base_dir}...")
            for root, dirs, files in os.walk(local_dir_path):
                relative_path = os.path.relpath(root, local_dir_path)
                remote_current_dir = remote_base_dir if relative_path == "." else os.path.join(remote_base_dir, relative_path).replace("\\", "/")
                if relative_path != ".": self._ensure_remote_dir_internal(sftp, remote_current_dir)
                for filename in files:
                    local_file = os.path.join(root, filename)
                    remote_file = os.path.join(remote_current_dir, filename).replace("\\", "/")
                    print(f"INFO:   Uploading {local_file} -> {remote_file}")
                    sftp.put(local_file, remote_file)
                    if return_remote_paths:
                        local_relative = os.path.relpath(local_file, local_dir_path).replace("\\", "/")
                        uploaded_paths[local_relative] = remote_file
            print(f"INFO: Directory upload successful.")
        return uploaded_paths

def create_sftp_service_from_env() -> SFTPFileStorageService:
    # 以前の実装と同じ
    print("INFO: Initializing SFTPFileStorageService from env...")
    try:
        vps_ip=os.environ["VPS_IP"]; vps_user=os.environ["VPS_USER"]
        vps_account_password=os.environ["VPS_ACCOUNT_PASSWORD"]
        key_file_path=os.environ["VPS_KEY_FILE_PATH"]
        vps_port=int(os.environ.get("VPS_PORT", 22))
        remote_training_dir=os.environ.get("VPS_TRAINING_DIR", f"/home/{vps_user}/training_data")
        remote_model_dir=os.environ.get("VPS_MODEL_DIR", f"/home/{vps_user}/models")
        return SFTPFileStorageService( vps_ip=vps_ip, vps_user=vps_user, vps_account_password=vps_account_password,
                                       key_file_path=key_file_path, remote_training_dir=remote_training_dir,
                                       remote_model_dir=remote_model_dir, vps_port=vps_port )
    except KeyError as e: msg = f"FATAL: Missing env var for SFTP: {e}"; print(msg); raise EnvironmentError(msg)
    except Exception as e: msg = f"FATAL: Failed to init SFTPService: {e}"; print(msg); raise

# === End SFTP Client Implementation ===


# === Domain/Repo Imports (Adjust paths as needed) ===
try:
    from domain.entities.finetuning_job import FinetuningJob
    from domain.value_objects.id import ID
    from domain.entities.weight_visualization import WeightVisualization, NewWeightVisualization
    from domain.value_objects.visualization_details import LayerVisualization, WeightDetail
    from infrastructure.database.mysql.finetuning_job_repository import MySQLFinetuningJobRepository
    from worker.repository.weight_visualization_repository import MySQLWeightVisualizationRepository
except ImportError as e:
    print(f"WARN: Using dummy imports/classes due to ImportError: {e}")
    # (Dummy class definitions from previous response)
    class ID:
        def __init__(self, value): self.value = value
    @dataclass
    class FinetuningJob: id: ID; agent_id: ID; training_file_path: str; status: str; created_at: Any; finished_at: Optional[Any]; error_message: Optional[str]
    @dataclass(frozen=True)
    class WeightDetail: name: str; before_url: str; after_url: str; delta_url: str
    @dataclass(frozen=True)
    class LayerVisualization: layer_name: str; weights: List[WeightDetail]
    @dataclass
    class WeightVisualization: job_id: ID; layers: List[LayerVisualization] = field(default_factory=list)
    def NewWeightVisualization(*args, **kwargs): return WeightVisualization(ID(0))
    class MySQLFinetuningJobRepository:
        def find_by_id(self, job_id): print(f"DB MOCK: Finding Job {job_id.value}"); return FinetuningJob(id=job_id, agent_id=ID(0), training_file_path='', status='queued', created_at=PythonDateTime.utcnow(), finished_at=None, error_message=None)
        def update_job(self, job): print(f"DB MOCK: Updating Job {job.id.value} to status {job.status}")
    class MySQLWeightVisualizationRepository:
        def save(self, vis): print(f"DB MOCK: Saving Visualization for Job {vis.job_id.value}")


# === Helper Function (_parse_visualization_output) ===
def _parse_visualization_output(uploaded_image_paths: Dict[str, str], job_id: int) -> List[Dict[str, Any]]:
    """可視化画像のパス辞書をDB保存用の形式に変換"""
    # (Implementation is the same as previous response)
    layers_dict: Dict[str, Dict[str, Any]] = {}
    for local_rel_path, remote_url in uploaded_image_paths.items():
        parts = local_rel_path.split(os.sep);
        if len(parts) < 2: continue
        layer_dir_name, file_name = parts[0], parts[-1]
        match = re.match(r"(.*)_(before|after|delta)\.png", file_name)
        if not match: continue
        weight_name_base, image_type = match.group(1).replace('_', '.'), match.group(2)
        if layer_dir_name not in layers_dict: layers_dict[layer_dir_name] = {"layer_name": layer_dir_name, "weights": {}}
        if weight_name_base not in layers_dict[layer_dir_name]["weights"]: layers_dict[layer_dir_name]["weights"][weight_name_base] = {"name": weight_name_base}
        layers_dict[layer_dir_name]["weights"][weight_name_base][f"{image_type}_url"] = remote_url
    final_layers_data = []
    for layer_name, layer_data in layers_dict.items():
        weights_list = list(layer_data.get("weights", {}).values())
        if weights_list: final_layers_data.append({"layer_name": layer_name, "weights": weights_list})
    return final_layers_data

# === Pipeline Step Functions ===

def _update_job_status(job_repo: MySQLFinetuningJobRepository, job_id: ID, status: str, 
                       finished_at: Optional[PythonDateTime] = None, error_message: Optional[str] = None) -> Optional[FinetuningJob]:
    """ヘルパー: ジョブステータスと関連情報をDBに更新"""
    try:
        job_to_update = job_repo.find_by_id(job_id)
        if not job_to_update:
            print(f"ERROR: Job {job_id.value}: Cannot update status, job not found.")
            return None
        
        # Update fields
        job_to_update.status = status
        if finished_at: job_to_update.finished_at = finished_at
        # Only update error message if a new one is provided and none exists, or explicitly overwrite
        if error_message and not job_to_update.error_message: 
             job_to_update.error_message = error_message[:1000] # Limit length
        elif error_message: # Overwrite if needed
             job_to_update.error_message = error_message[:1000]
        
        job_repo.update_job(job_to_update)
        print(f"INFO: Job {job_id.value}: Status updated to '{status}'.")
        return job_to_update
    except Exception as e:
        print(f"ERROR: Job {job_id.value}: CRITICAL - Failed to update DB status to '{status}': {e}")
        # Depending on severity, you might want to re-raise here
        return None # Indicate failure

def _run_script(job_id: int, script_path: str, args: List[str], cwd: str) -> bool:
    """ヘルパー: 外部Pythonスクリプトを実行し、成否を返す"""
    if not os.path.isfile(script_path):
        print(f"ERROR: Job {job_id}: Script not found: {script_path}")
        return False # Indicate failure
        
    command = ["python", script_path] + args
    print(f"INFO: Job {job_id}: Executing command: {' '.join(command)}")
    try:
        process_result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd) # check=True でエラー時例外発生
        print(f"--- Script STDOUT ---\n{process_result.stdout}\n---------------------")
        print(f"INFO: Job {job_id}: Script '{os.path.basename(script_path)}' executed successfully.")
        return True # Indicate success
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Job {job_id}: Script '{os.path.basename(script_path)}' failed!")
        print(f"--- Script STDERR ---\n{e.stderr}\n---------------------")
        print(f"--- Script STDOUT ---\n{e.stdout}\n---------------------")
        return False # Indicate failure
    except Exception as e:
        print(f"ERROR: Job {job_id}: Failed to run script '{os.path.basename(script_path)}': {e}")
        return False

# === Main Pipeline Function ===
def execute_finetuning_pipeline(
    job_id: int,
    training_file_path_on_vps: str,
    base_model_name_short: str,
    job_repo: MySQLFinetuningJobRepository,
    visualization_repo: MySQLWeightVisualizationRepository,
    file_storage_service: SFTPFileStorageService,
    worker_base_dir: str = "/app/worker"
    ) -> None:
    """ファインチューニングジョブの実行パイプライン"""

    # --- 0. Setup ---
    print(f"INFO: Job {job_id}: Pipeline starting for model '{base_model_name_short}'...")
    job_id_obj = ID(job_id)
    final_status = 'failed' # Default to failed unless explicitly completed
    final_error_message: Optional[str] = None
    
    # Paths
    base_model_local_path = os.path.join(worker_base_dir, "tasks", "finetuning", "models", base_model_name_short)
    temp_job_dir = f"/tmp/job_{job_id}"
    temp_data_dir = os.path.join(temp_job_dir, "data")
    temp_model_dir = os.path.join(temp_job_dir, "model")
    temp_visuals_dir = os.path.join(temp_job_dir, "visuals")
    local_training_file_path = os.path.join(temp_data_dir, os.path.basename(training_file_path_on_vps))
    remote_model_base_dir = os.path.join(file_storage_service.remote_model_base_dir, f"job_{job_id}").replace("\\", "/")
    remote_visuals_base_dir = os.path.join(file_storage_service.remote_visuals_base_dir, f"job_{job_id}").replace("\\", "/")
    train_script_path = os.path.join(worker_base_dir, "tasks", "finetuning", "train_and_export.py")
    visualize_script_path = os.path.join(worker_base_dir, "tasks", "finetuning", "visualize_finetuning_diff.py")

    # Initial Cleanup
    if os.path.exists(temp_job_dir):
        print(f"WARN: Job {job_id}: Cleaning up existing temp dir {temp_job_dir}...")
        try: shutil.rmtree(temp_job_dir)
        except Exception as clean_e: print(f"WARN: Job {job_id}: Failed initial cleanup: {clean_e}")
    try:
        os.makedirs(temp_data_dir, exist_ok=True)
        os.makedirs(temp_model_dir, exist_ok=True)
        os.makedirs(temp_visuals_dir, exist_ok=True)
    except Exception as mkdir_e:
         print(f"ERROR: Job {job_id}: Failed to create temp directories: {mkdir_e}")
         _update_job_status(job_repo, job_id_obj, 'failed', PythonDateTime.utcnow(), f"Worker setup error: {mkdir_e}")
         return # Cannot proceed

    try:
        # --- 1. Update Status to Running ---
        if not _update_job_status(job_repo, job_id_obj, 'running'):
             raise RuntimeError("Failed to set job status to 'running'. Cannot proceed.") # Raise to stop

        # --- 2. Download Training File ---
        print(f"INFO: Job {job_id}: Downloading training file...")
        file_storage_service.download_file(training_file_path_on_vps, local_training_file_path)
        print(f"INFO: Job {job_id}: Training file downloaded.")

        # --- 3. Run Training Script ---
        print(f"INFO: Job {job_id}: Starting training script...")
        train_args = ["--base_model_path", base_model_local_path, "--training_file", local_training_file_path, "--output_dir", temp_model_dir]
        training_successful = _run_script(job_id, train_script_path, train_args, worker_base_dir)
        if not training_successful:
             raise RuntimeError("Training script failed.") # Raise to stop and record error

        # --- 4. Process Results (if training succeeded) ---
        print(f"INFO: Job {job_id}: Processing successful training results...")
        
        # 4a. Upload Model
        print(f"INFO: Job {job_id}: Uploading model artifacts...")
        file_storage_service.upload_directory(temp_model_dir, remote_model_base_dir)
        print(f"INFO: Job {job_id}: Model artifacts uploaded.")

        # 4b. Run Visualization (Optional Failure)
        print(f"INFO: Job {job_id}: Running visualization script...")
        vis_args = ["--base_model_path", base_model_local_path, "--finetuned_model_path", temp_model_dir, "--output_dir", temp_visuals_dir]
        vis_successful = _run_script(job_id, visualize_script_path, vis_args, worker_base_dir)
        
        if vis_successful:
            # 4c. Upload Visualizations (Optional Failure)
            print(f"INFO: Job {job_id}: Uploading visualization images...")
            try:
                uploaded_image_paths = file_storage_service.upload_directory(
                    temp_visuals_dir, remote_visuals_base_dir, return_remote_paths=True
                )
                print(f"INFO: Job {job_id}: Visualization images uploaded.")
                
                # 4d. Save Visualization Data to DB (Optional Failure)
                print(f"INFO: Job {job_id}: Formatting and saving visualization data...")
                layers_data = _parse_visualization_output(uploaded_image_paths, job_id)
                if layers_data:
                    try:
                        vis_entity = NewWeightVisualization(job_id=job_id, layers_data=layers_data)
                        visualization_repo.save(vis_entity)
                        print(f"INFO: Job {job_id}: Visualization data saved.")
                    except Exception as vis_save_e: print(f"WARN: Job {job_id}: Failed save vis data: {vis_save_e}")
                else: print(f"WARN: Job {job_id}: No vis data formatted for DB.")
            except Exception as vis_upload_e: print(f"WARN: Job {job_id}: Failed upload vis images: {vis_upload_e}")
        else:
             print(f"WARN: Job {job_id}: Skipping visualization upload/save due to script failure.")

        # If we reach here, training and model upload were successful
        final_status = 'completed'

    # --- Error Handling for Pipeline Steps ---
    except FileNotFoundError as e: final_error_message = f"File not found error: {str(e)[:1000]}"
    except FileStorageError as e: final_error_message = f"Storage error: {str(e)[:1000]}"
    except RuntimeError as e: final_error_message = f"Script execution error: {str(e)[:1000]}"
    except Exception as e:
        import traceback; traceback.print_exc()
        final_error_message = f"Unexpected pipeline error: {str(e)[:1000]}"
    
    if final_error_message: print(f"ERROR: Job {job_id}: {final_error_message}")

    # --- Update Final Status (Always Attempt) ---
    finished_time = PythonDateTime.utcnow()
    _update_job_status(job_repo, job_id_obj, final_status, finished_time, final_error_message)

    # --- Cleanup (Always Attempt) ---
    print(f"INFO: Job {job_id}: Cleaning up temp dir {temp_job_dir}...")
    try:
        if os.path.exists(temp_job_dir): shutil.rmtree(temp_job_dir)
        print(f"INFO: Job {job_id}: Temp dir cleaned up.")
    except Exception as clean_e: print(f"WARN: Job {job_id}: Failed cleanup: {clean_e}")

    # --- End Log ---
    print(f"INFO: Job {job_id}: Pipeline finished with status '{final_status}'.")

# === Celery Task (Example in finetuning_tasks.py) ===
# (Needs adjustment for importing concrete classes and the local SFTP factory)
# from celery_app import celery_app
# ... (rest of imports) ...
# from worker.tasks.finetuning.executor import create_sftp_service_from_env, execute_finetuning_pipeline

# @celery_app.task(...)
# def run_finetuning_job_task(...):
#     # ... Initialize repos and service ...
#     try:
#         execute_finetuning_pipeline(...)
#     except Exception as e:
#         # ... Celery error/retry handling ...
#         raise e