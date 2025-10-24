from domain.services.job_queue_domain_service import JobQueueDomainService
from typing import Optional
from celery import Celery # Celery本体をインポート
import os
from decouple import config # 環境変数読み込みのため

# -----------------------------------------------------------------
# 1. Celery クライアントの初期化 (このファイル内で完結)
# -----------------------------------------------------------------
# Web API側でCeleryクライアントを初期化
# 環境変数 CELERY_BROKER_URL を使用して設定します。

# 環境変数から設定を取得
# .env や Docker Compose で設定されている CELERY_BROKER_URL を使用
BROKER_URL = os.getenv('CELERY_BROKER_URL', config('CELERY_BROKER_URL', default='redis://redis:6379/0'))

celery_client = Celery(
    'agenthub_client', # クライアントアプリケーション名
    broker=BROKER_URL
)
# 注意: backendはDBや他の依存関係は必要ありません。Redisへの接続情報のみが必要です。
# -----------------------------------------------------------------


class CeleryJobQueueDomainServiceImpl(JobQueueDomainService):
    """
    JobQueueDomainService の Celery 向け実装。
    タスク名を文字列で指定し、キューに投入する責務を持つ。
    """
    def __init__(self):
        # コンストラクタでクライアントの初期化は不要 (ファイルレベルで既に完了しているため)
        pass

    def enqueue_finetuning_job(self, job_id: int, file_path: str) -> None:
        """
        Celeryのタスク名を指定し、非同期キューに投入する。
        """
        # ★ Workerコンテナのタスク定義ファイルで指定したタスク名を使用 ★
        TASK_NAME = 'finetuning.submit_job' 
        
        try:
            # send_task() メソッドで文字列名を指定してキューにプッシュ
            celery_client.send_task(
                TASK_NAME,
                args=(job_id, file_path), # タスクが受け取る引数
                kwargs={}
            )
            
        except Exception as e:
            # Celery/Redisへの接続失敗など
            print(f"ERROR: Failed to enqueue job {job_id} to Celery broker. {e}")
            raise RuntimeError(f"Failed to submit job to worker queue: {e}")


def NewJobQueueDomainService() -> JobQueueDomainService:
    """JobQueueDomainService のファクトリ関数"""
    # Celeryの初期化がファイルロード時に行われていることを前提にインスタンスを返す
    return CeleryJobQueueDomainServiceImpl()