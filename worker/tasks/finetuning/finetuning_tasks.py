# AGENTHUB/worker/tasks/finetuning/finetuning_tasks.py

from worker.celery_app import celery_app
from . import executor # ロジックを実装する executor モジュールをインポート

# タスク名: finetuning.submit_job
@celery_app.task(bind=True, name='finetuning.submit_job')
def submit_finetuning_job(self, job_id: str, file_path: str):
    """
    ユーザーリクエストに応じて、ファインチューニングジョブを開始するタスク。
    長時間処理は executor に委譲する。
    """
    try:
        # executor に処理を委譲し、ジョブを実行・DBステータスを更新させる
        executor.execute_finetuning_pipeline(job_id, file_path)
        
    except Exception as e:
        # 処理中にエラーが発生した場合、タスクを失敗としてマーク
        print(f"Fine-tuning job {job_id} failed: {e}")
        # executor や repository 経由で DB のステータスを 'failed' に更新するロジックをここに実装
        # 例: executor.update_job_status(job_id, 'failed', error=str(e))
        raise # Celeryにタスクの失敗を通知