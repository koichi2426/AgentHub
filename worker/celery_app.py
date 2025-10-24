# AGENTHUB/worker/celery_app.py

from celery import Celery
import os
from decouple import config 

# 環境変数が設定されていない場合に例外を発生させるよう、default引数を設定しない。
try:
    # 環境変数からのみ設定値を取得
    BROKER_URL = config('CELERY_BROKER_URL')
    BACKEND_URL = config('CELERY_RESULT_BACKEND')
except Exception as e:
    # 設定ミスを早期に検出するため、クラッシュさせる
    print("FATAL ERROR: Celery environment variables CELERY_BROKER_URL and CELERY_RESULT_BACKEND must be set.")
    raise EnvironmentError("Celery environment configuration is missing.") from e

# Celeryアプリケーションのインスタンス化
celery_app = Celery(
    'agenthub_worker', # アプリケーション名
    broker=BROKER_URL, 
    backend=BACKEND_URL
)

# Celeryの設定
celery_app.conf.update(
    # タスクのシリアライザと結果のシリアライザを JSON に設定
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    # タイムゾーンは、環境変数や設定ファイルから取得するのが理想だが、ここではコードベースでの標準を設定
    timezone='Asia/Tokyo',
    enable_utc=True,
    
    # ★ 修正: タスク定義ファイルへの完全なパスを指定し、ワーカーがタスクを認識できるようにする ★
    include=[
        'worker.tasks.finetuning.finetuning_tasks', 
        'worker.tasks.deployment.deployment_tasks', 
    ]
)