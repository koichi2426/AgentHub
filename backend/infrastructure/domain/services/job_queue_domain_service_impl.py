from domain.services.job_queue_domain_service import JobQueueDomainService
from typing import Optional
from celery import Celery # Celery本体をインポート
import os
from decouple import config # 環境変数読み込みのため

# -----------------------------------------------------------------
# 1. Celery クライアントの初期化 (このファイル内で完結)
# -----------------------------------------------------------------
# 環境変数から設定を取得
BROKER_URL = os.getenv('CELERY_BROKER_URL', config('CELERY_BROKER_URL', default='redis://redis:6379/0'))

celery_client = Celery(
    'agenthub_client', # クライアントアプリケーション名
    broker=BROKER_URL
)
# -----------------------------------------------------------------


class CeleryJobQueueDomainServiceImpl(JobQueueDomainService):
    """
    JobQueueDomainService の Celery 向け実装。
    タスク名を文字列で指定し、キューに投入する責務を持つ。
    """
    def __init__(self):
        pass

    def enqueue_finetuning_job(self, job_id: int, file_path: str) -> None:
        """
        指定されたファインチューニングジョブを非同期キューに投入する。
        """
        TASK_NAME = 'finetuning.submit_job' 
        
        try:
            celery_client.send_task(
                TASK_NAME,
                args=(job_id, file_path),
                kwargs={}
            )
            
        except Exception as e:
            print(f"ERROR: Failed to enqueue finetuning job {job_id} to Celery broker. {e}")
            raise RuntimeError(f"Failed to submit finetuning job to worker queue: {e}")

    def enqueue_deployment_job(self, job_id: int, model_path: str) -> None:
        """
        指定されたデプロイメントジョブを非同期キューに投入する。
        """
        TASK_NAME = 'deployment.deploy_model' 
        
        try:
            celery_client.send_task(
                TASK_NAME,
                args=(job_id, model_path),
                kwargs={}
            )
            
        except Exception as e:
            print(f"ERROR: Failed to enqueue deployment job {job_id} to Celery broker. {e}")
            raise RuntimeError(f"Failed to submit deployment job to worker queue: {e}")
            
    def enqueue_engine_test_job(self, job_id: int, deployment_id: int, test_data_path: str) -> None:
        """
        指定されたエンジンテストジョブを非同期キューに投入する。
        """
        # エンジンテスト用のタスク名を定義
        TASK_NAME = 'engine.run_test' 
        
        try:
            # model_pathをdeployment_idに変更
            celery_client.send_task(
                TASK_NAME,
                args=(job_id, deployment_id, test_data_path), 
                kwargs={}
            )
            
        except Exception as e:
            # Celery/Redisへの接続失敗など
            print(f"ERROR: Failed to enqueue engine test job {job_id} to Celery broker. {e}")
            raise RuntimeError(f"Failed to submit engine test job to worker queue: {e}")


def NewJobQueueDomainService() -> JobQueueDomainService:
    """JobQueueDomainService のファクトリ関数"""
    return CeleryJobQueueDomainServiceImpl()