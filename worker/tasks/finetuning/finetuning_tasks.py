# AGENTHUB/worker/tasks/finetuning/finetuning_tasks.py

from worker.celery_app import celery_app
from . import executor # executor モジュールをインポート

# タスク名: finetuning.submit_job
@celery_app.task(bind=True, name='finetuning.submit_job', max_retries=1)
# ★★★ base_model_name_short 引数を削除 ★★★
def submit_finetuning_job(self, job_id: int, file_path: str):
    """
    ファインチューニングジョブを開始するタスク。
    executor.execute_finetuning_pipeline に処理を委譲する。
    モデルは常に 'bert-tiny' を使用する。
    """
    try:
        print(f"INFO: Celery task received for job {job_id} (using default model 'bert-tiny')")
        # executor に処理を委譲
        executor.execute_finetuning_pipeline(
            job_id=int(job_id),
            training_file_path_on_vps=file_path
            # ★★★ base_model_name_short は渡さない ★★★
        )
        print(f"INFO: Celery task for job {job_id} completed via executor.")

    except Exception as e:
        print(f"ERROR: Celery task for job {job_id} failed critically: {e}")
        # executor の finally ブロックで DB 更新されるはず
        raise self.retry(exc=e, countdown=60) if self.request.retries < self.max_retries else e