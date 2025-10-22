# AGENTHUB/worker/celery_app.py

from celery import Celery
import os
from decouple import config # 環境変数を扱うライブラリ（Python-decoupleなどを想定）

# 環境変数から設定を取得
# Docker Composeで定義されたサービス名 'redis' を使用
BROKER_URL = os.getenv('CELERY_BROKER_URL', config('CELERY_BROKER_URL', default='redis://localhost:6379/0'))
BACKEND_URL = os.getenv('CELERY_RESULT_BACKEND', config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0'))

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
    # タイムゾーンを東京に設定
    timezone='Asia/Tokyo',
    enable_utc=True,
    
    # ★ 拡張性のための設定: tasks パッケージ内の全てのタスクを自動検出 ★
    # 新しいタスクモジュール (finetuning/, deployment/) を追加しても、自動で認識されます。
    # ここで指定する 'worker.tasks' は、AGENDHUB/worker/tasks/ ディレクトリを指します。
    include=['worker.tasks'] 
)

# autodiscover_tasks を使用する代わりに、include で明示的に指定することで、
# Workerが起動する際に worker/tasks/ 以下の全タスクをロードします。
# celery_app.autodiscover_tasks(['worker.tasks']) # (こちらも使用可能)