# AGENTHUB/worker/tasks/finetuning/finetuning_tasks.py

from worker.celery_app import celery_app
from . import executor # executor モジュールをインポート

# タスク名: finetuning.submit_job
@celery_app.task(bind=True, name='finetuning.submit_job', max_retries=1) # リトライ設定例
def submit_finetuning_job(self, job_id: int, file_path: str, base_model_name_short: str):
    """
    ファインチューニングジョブを開始するタスク。
    executor.execute_finetuning_pipeline に処理を委譲する。
    """
    try:
        print(f"INFO: Celery task received for job {job_id} with model {base_model_name_short}")
        # executor に処理を委譲
        # job_id は int 型に変換 (Celery が str で渡してくる場合があるため念のため)
        executor.execute_finetuning_pipeline(
            job_id=int(job_id),
            training_file_path_on_vps=file_path,
            base_model_name_short=base_model_name_short
        )
        print(f"INFO: Celery task for job {job_id} completed via executor.")

    except Exception as e:
        # executor 内の finally ブロックで DB ステータス更新が試みられるはずだが、
        # ここでエラーが発生した場合（設定ミス、インポートエラーなど）は
        # Celery に失敗を通知し、リトライさせる（設定されていれば）。
        print(f"ERROR: Celery task for job {job_id} failed critically: {e}")
        # executor.py 内の finally で DB 更新が失敗した場合のフォールバック更新は
        # ここで行うこともできるが、複雑になるため executor 側に任せるのが基本。
        raise self.retry(exc=e, countdown=60) if self.request.retries < self.max_retries else e