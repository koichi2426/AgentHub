import os
import shutil
from datetime import datetime as PythonDateTime
import time
import subprocess
import json
import re
from typing import Optional, List, Dict, Any

# --- Import from sibling modules ---
try:
    from .sftp_service import create_sftp_service_from_env, SFTPFileStorageService, FileStorageError
    from .db_helpers import find_job_by_id, update_job_status, save_visualization, JobInfo
    # 修正: utils から extract_methods_from_training_file をインポート
    from .utils import parse_visualization_output, run_script, extract_methods_from_training_file
except ImportError as e:
    print(f"FATAL: Failed to import sibling modules: {e}")
    raise


def execute_finetuning_pipeline(
    job_id: int,
    training_file_path_on_vps: str,
    worker_base_dir: str = "/app/worker"
) -> None:
    """
    ファインチューニングジョブ実行パイプライン (スタンドアロン実装)。
    モデルは 'bert-tiny' を固定で使用する。
    """

    # --- 0. Setup ---
    base_model_name_short = 'bert-tiny'
    print(f"INFO: Job {job_id}: Pipeline starting for fixed model '{base_model_name_short}'...")
    final_error_message: Optional[str] = None
    sftp_service: Optional[SFTPFileStorageService] = None

    # Paths
    base_model_local_path = os.path.join(worker_base_dir, "tasks", "finetuning", "models", base_model_name_short)
    temp_job_dir = f"/tmp/job_{job_id}"
    temp_data_dir = os.path.join(temp_job_dir, "data")
    temp_model_dir = os.path.join(temp_job_dir, "model")
    temp_visuals_dir = os.path.join(temp_job_dir, "visuals")
    local_training_file_path = os.path.join(temp_data_dir, os.path.basename(training_file_path_on_vps))
    
    # ★★★ 新規: ローカルメソッドファイルパス定義 ★★★
    local_methods_file_path = os.path.join(temp_model_dir, "methods.txt")
    
    train_script_path = os.path.join(worker_base_dir, "tasks", "finetuning", "train_and_export.py")
    visualize_script_path = os.path.join(worker_base_dir, "tasks", "finetuning", "visualize_finetuning_diff.py")

    # Initial Cleanup & Dir Creation
    if os.path.exists(temp_job_dir):
        print(f"WARN: Job {job_id}: Cleaning up existing temp dir...")
        try:
            shutil.rmtree(temp_job_dir)
        except Exception as e:
            print(f"WARN: Job {job_id}: Failed initial cleanup: {e}")

    try:
        os.makedirs(temp_data_dir, exist_ok=True)
        os.makedirs(temp_model_dir, exist_ok=True)
        os.makedirs(temp_visuals_dir, exist_ok=True)
    except Exception as e:
        print(f"ERROR: Job {job_id}: Failed to create temp dirs: {e}")
        try:
            update_job_status(job_id, 'failed', PythonDateTime.utcnow(), f"Worker setup error: {e}")
        except Exception:
            pass
        return

    try:
        # --- Instantiate SFTP Service ---
        sftp_service = create_sftp_service_from_env()
        remote_model_base_dir = os.path.join(sftp_service.remote_model_base_dir, f"job_{job_id}").replace("\\", "/")
        remote_visuals_base_dir = os.path.join(sftp_service.remote_visuals_base_dir, f"job_{job_id}").replace("\\", "/")

        # --- Base Model Check ---
        if not os.path.isdir(base_model_local_path):
            raise FileNotFoundError(f"Base model directory not found locally: {base_model_local_path}")

        # --- 1. Update Status to Running ---
        print(f"INFO: Job {job_id}: Updating status to 'running'...")
        job_info = find_job_by_id(job_id)
        if not job_info:
            raise ValueError(f"Job ID {job_id} not found.")
        update_job_status(job_id, 'running', error_message=None, finished_at=None)
        print(f"INFO: Job {job_id}: Status set to 'running'.")

        # --- 2. Download Training File ---
        print(f"INFO: Job {job_id}: Downloading training file...")
        sftp_service.download_file(training_file_path_on_vps, local_training_file_path)
        print(f"INFO: Job {job_id}: Training file downloaded.")

        # ★★★ 2.5. Extract Methods from Training File ★★★
        print(f"INFO: Job {job_id}: Extracting methods...")
        extract_methods_from_training_file(local_training_file_path, local_methods_file_path)
        print(f"INFO: Job {job_id}: Method extraction complete.")
        
        # --- 3. Run Training Script ---
        print(f"INFO: Job {job_id}: Starting training script...")
        train_args = [
            "--base_model_path", base_model_local_path,
            "--training_file", local_training_file_path,
            "--output_dir", temp_model_dir
        ]
        run_script(job_id, train_script_path, train_args, worker_base_dir)
        print(f"INFO: Job {job_id}: Training script successful.")

        # --- 4. Process Results ---
        print(f"INFO: Job {job_id}: Processing successful training results...")

        # 4a. Upload Model (methods.txtもtemp_model_dirにあるため、一緒にアップロードされる)
        print(f"INFO: Job {job_id}: Uploading model artifacts (including methods.txt)...")
        sftp_service.upload_directory(temp_model_dir, remote_model_base_dir)
        print(f"INFO: Job {job_id}: Model artifacts uploaded.")

        # 4b. Run Visualization
        print(f"INFO: Job {job_id}: Running visualization script...")
        vis_args = [
            "--base_model_path", base_model_local_path,
            "--finetuned_model_path", temp_model_dir,
            "--output_dir", temp_visuals_dir
        ]
        try:
            vis_successful = run_script(job_id, visualize_script_path, vis_args, worker_base_dir)
            if vis_successful:
                print(f"INFO: Job {job_id}: Uploading visualization images...")
                uploaded_image_paths = sftp_service.upload_directory(
                    temp_visuals_dir, remote_visuals_base_dir, return_remote_paths=True
                )
                print(f"INFO: Job {job_id}: Vis images uploaded ({len(uploaded_image_paths)} files).")

                # Save visualization data
                layers_data = parse_visualization_output(uploaded_image_paths, job_id)
                if layers_data:
                    save_visualization(job_id, layers_data)
                else:
                    print(f"WARN: Job {job_id}: No vis data formatted for DB.")
            else:
                print(f"WARN: Job {job_id}: Vis script failed. Skipping vis processing.")
        except FileNotFoundError as e:
            print(f"WARN: Job {job_id}: Vis script not found, skipping: {e}")
        except Exception as e:
            print(f"WARN: Job {job_id}: Unexpected error during vis: {e}")

    except (FileNotFoundError, FileStorageError, RuntimeError, ValueError, ConnectionError, EnvironmentError) as e:
        final_error_message = f"{type(e).__name__}: {str(e)[:1000]}"
        print(f"ERROR: Job {job_id}: Pipeline failed - {final_error_message}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        final_error_message = f"Unexpected error: {str(e)[:1000]}"
        print(f"ERROR: Job {job_id}: Pipeline failed - {final_error_message}")

    finally:
        finished_time = PythonDateTime.utcnow()
        final_status_to_set = 'failed' if final_error_message else 'completed'

        try:
            print(f"INFO: Job {job_id}: Updating final status to '{final_status_to_set}'...")
            update_job_status(job_id, final_status_to_set, finished_time, final_error_message)
        except Exception as db_update_e:
            print(f"ERROR: Job {job_id}: CRITICAL - Failed to update final DB status: {db_update_e}")

        print(f"INFO: Job {job_id}: Cleaning up temp dir {temp_job_dir}...")
        try:
            if os.path.exists(temp_job_dir):
                shutil.rmtree(temp_job_dir)
            print(f"INFO: Job {job_id}: Temp dir cleaned up.")
        except Exception as clean_e:
            print(f"WARN: Job {job_id}: Failed cleanup: {clean_e}")

        print(f"INFO: Job {job_id}: Pipeline finished with status '{final_status_to_set}'.")