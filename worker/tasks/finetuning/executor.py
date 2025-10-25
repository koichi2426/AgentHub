# worker/tasks/finetuning/executor.py

import time
import os
import shutil
from datetime import datetime as PythonDateTime
from typing import Optional, List, Dict, Any

# --- Import from sibling modules ---
try:
    from .sftp_service import create_sftp_service_from_env, SFTPFileStorageService, FileStorageError
    from .db_helpers import find_job_by_id, update_job_status, save_visualization, JobInfo, close_db_pool # Added close_db_pool
    from .utils import parse_visualization_output, run_script
except ImportError as e:
    print(f"FATAL: Failed to import sibling modules: {e}")
    raise # Cannot proceed without helpers

# === Main Pipeline Function ===
def execute_finetuning_pipeline(
    job_id: int,
    training_file_path_on_vps: str,
    base_model_name_short: str,
    worker_base_dir: str = "/app/worker" # Default path inside container
    ) -> None:
    """
    ファインチューニングジョブ実行パイプライン (スタンドアロン実装)。
    ヘルパーモジュールを利用して処理を実行する。
    """

    # --- 0. Setup ---
    print(f"INFO: Job {job_id}: Pipeline starting for model '{base_model_name_short}'...")
    final_status = 'failed' # Default to failed unless explicitly completed
    final_error_message: Optional[str] = None
    sftp_service: Optional[SFTPFileStorageService] = None # Hold service instance

    # Paths
    base_model_local_path = os.path.join(worker_base_dir, "tasks", "finetuning", "models", base_model_name_short)
    temp_job_dir = f"/tmp/job_{job_id}"
    temp_data_dir = os.path.join(temp_job_dir, "data")
    temp_model_dir = os.path.join(temp_job_dir, "model")
    temp_visuals_dir = os.path.join(temp_job_dir, "visuals")
    local_training_file_path = os.path.join(temp_data_dir, os.path.basename(training_file_path_on_vps))
    train_script_path = os.path.join(worker_base_dir, "tasks", "finetuning", "train_and_export.py")
    visualize_script_path = os.path.join(worker_base_dir, "tasks", "finetuning", "visualize_finetuning_diff.py")
    remote_model_base_dir = "" # Will be set after sftp_service is initialized
    remote_visuals_base_dir = "" # Will be set after sftp_service is initialized

    # Initial Cleanup & Dir Creation (Moved earlier before potential service init fail)
    if os.path.exists(temp_job_dir):
        print(f"WARN: Job {job_id}: Cleaning up existing temp dir...");
        try: shutil.rmtree(temp_job_dir)
        except Exception as e: print(f"WARN: Job {job_id}: Failed initial cleanup: {e}")
    try:
        os.makedirs(temp_data_dir, exist_ok=True); os.makedirs(temp_model_dir, exist_ok=True); os.makedirs(temp_visuals_dir, exist_ok=True)
    except Exception as e:
         print(f"ERROR: Job {job_id}: Failed create temp dirs: {e}")
         # Try to update DB even without full repo object
         try: update_job_status(job_id, 'failed', PythonDateTime.utcnow(), f"Worker setup error: {e}")
         except Exception: pass # Ignore if DB update fails here
         return # Cannot proceed

    try:
        # --- Instantiate SFTP Service ---
        sftp_service = create_sftp_service_from_env()
        # Define remote paths using the instantiated service config
        remote_model_base_dir = os.path.join(sftp_service.remote_model_base_dir, f"job_{job_id}").replace("\\", "/")
        remote_visuals_base_dir = os.path.join(sftp_service.remote_visuals_base_dir, f"job_{job_id}").replace("\\", "/")

        # --- Base Model Check ---
        if not os.path.isdir(base_model_local_path):
             raise FileNotFoundError(f"Base model directory not found locally: {base_model_local_path}")

        # --- 1. Update Status to Running ---
        print(f"INFO: Job {job_id}: Updating status to 'running'...")
        job_info = find_job_by_id(job_id)
        if not job_info: raise ValueError(f"Job ID {job_id} not found.")
        update_job_status(job_id, 'running', error_message=None, finished_at=None) # Reset error/finish
        print(f"INFO: Job {job_id}: Status set to 'running'.")

        # --- 2. Download Training File ---
        print(f"INFO: Job {job_id}: Downloading training file...")
        sftp_service.download_file(training_file_path_on_vps, local_training_file_path)
        print(f"INFO: Job {job_id}: Training file downloaded.")

        # --- 3. Run Training Script ---
        print(f"INFO: Job {job_id}: Starting training script...")
        train_args = ["--base_model_path", base_model_local_path, "--training_file", local_training_file_path, "--output_dir", temp_model_dir]
        # run_script raises RuntimeError on failure
        run_script(job_id, train_script_path, train_args, worker_base_dir)
        training_successful = True # If run_script didn't raise, it succeeded
        print(f"INFO: Job {job_id}: Training script successful.")

        # --- 4. Process Results (if training succeeded) ---
        print(f"INFO: Job {job_id}: Processing successful training results...")

        # 4a. Upload Model
        print(f"INFO: Job {job_id}: Uploading model artifacts...")
        sftp_service.upload_directory(temp_model_dir, remote_model_base_dir)
        print(f"INFO: Job {job_id}: Model artifacts uploaded.")

        # 4b. Run Visualization (Optional Failure - doesn't raise Exception from run_script but returns bool)
        print(f"INFO: Job {job_id}: Running visualization script...")
        vis_args = ["--base_model_path", base_model_local_path, "--finetuned_model_path", temp_model_dir, "--output_dir", temp_visuals_dir]
        try:
            vis_successful = run_script(job_id, visualize_script_path, vis_args, worker_base_dir)
            if vis_successful:
                # 4c. Upload Visualizations (Optional Failure)
                print(f"INFO: Job {job_id}: Uploading visualization images...")
                try:
                    uploaded_image_paths = sftp_service.upload_directory(
                        temp_visuals_dir, remote_visuals_base_dir, return_remote_paths=True
                    )
                    print(f"INFO: Job {job_id}: Visualization images uploaded ({len(uploaded_image_paths)} files).")

                    # 4d. Save Visualization Data to DB (Optional Failure)
                    print(f"INFO: Job {job_id}: Formatting and saving visualization data...")
                    layers_data = parse_visualization_output(uploaded_image_paths, job_id)
                    if layers_data:
                        save_visualization(job_id, layers_data) # Use direct DB helper
                    else: print(f"WARN: Job {job_id}: No vis data formatted for DB.")
                # Catch specific storage errors or general exceptions during vis processing
                except FileStorageError as e: print(f"WARN: Job {job_id}: Failed upload vis images: {e}")
                except Exception as e: print(f"WARN: Job {job_id}: Error processing vis results: {e}")
            else:
                 print(f"WARN: Job {job_id}: Visualization script failed. Skipping visualization processing.")
        except FileNotFoundError as e: # Catch if vis script itself is missing
             print(f"WARN: Job {job_id}: Visualization script not found, skipping: {e}")
        except RuntimeError as e: # Catch other execution errors from run_script for vis
             print(f"WARN: Job {job_id}: Visualization script execution failed: {e}")
        except Exception as e: # Catch unexpected errors during visualization steps
             print(f"WARN: Job {job_id}: Unexpected error during visualization: {e}")

        # If we reached here without critical exceptions (training script, model upload), mark as completed
        final_status = 'completed'

    # --- Error Handling ---
    except (FileNotFoundError, FileStorageError, RuntimeError, ValueError, ConnectionError, EnvironmentError) as e:
        final_error_message = f"{type(e).__name__}: {str(e)[:1000]}"
    except Exception as e:
        import traceback; traceback.print_exc()
        final_error_message = f"Unexpected error: {str(e)[:1000]}"

    if final_error_message: print(f"ERROR: Job {job_id}: Pipeline failed - {final_error_message}")

    # --- Update Final Status (Always Attempt) ---
    finished_time = PythonDateTime.utcnow()
    # Determine status based on whether an error message was set
    final_status_to_set = 'failed' if final_error_message else 'completed'
    try:
        print(f"INFO: Job {job_id}: Updating final status to '{final_status_to_set}'...")
        update_job_status(job_id, final_status_to_set, finished_time, final_error_message)
    except Exception as db_update_e:
        print(f"ERROR: Job {job_id}: CRITICAL - Failed to update final DB status: {db_update_e}")

    # --- Cleanup (Always Attempt) ---
    print(f"INFO: Job {job_id}: Cleaning up temp dir {temp_job_dir}...")
    try:
        if os.path.exists(temp_job_dir): shutil.rmtree(temp_job_dir)
        print(f"INFO: Job {job_id}: Temp dir cleaned up.")
    except Exception as clean_e: print(f"WARN: Job {job_id}: Failed cleanup: {clean_e}")

    # --- End Log ---
    print(f"INFO: Job {job_id}: Pipeline finished with status '{final_status_to_set}'.")

    # --- Close DB Pool (Optional - depends on worker lifecycle) ---
    # Consider calling this elsewhere if the worker process persists
    # close_db_pool()


# === How to Call (Example from Celery task in finetuning_tasks.py) ===
# (Adjust imports in finetuning_tasks.py)
# from worker.tasks.finetuning.executor import execute_finetuning_pipeline
#
# @celery_app.task(...)
# def run_finetuning_job_task(self, job_id: int, training_file_path_on_vps: str, base_model_name_short: str):
#     try:
#         execute_finetuning_pipeline(
#             job_id=job_id,
#             training_file_path_on_vps=training_file_path_on_vps,
#             base_model_name_short=base_model_name_short
#         )
#     except Exception as e:
#         print(f"ERROR: Celery task failed for job {job_id}: {e}")
#         # Pipeline's finally block should handle DB status update.
#         # Re-raise for Celery's retry/failure handling.
#         raise e
