# AGENTHUB/worker/Dockerfile

# 安定版のPythonイメージを使用
FROM python:3.10-slim

# 作業ディレクトリを設定
WORKDIR /app

# ----------------------------------------------------
# 1. 依存関係のインストール
# ----------------------------------------------------
# worker/requirements.txt をコピー
COPY requirements.txt .

# 必要なPythonパッケージをインストール (Celery, Redis, SQLAlchemy, DBコネクタなど)
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------
# 2. アプリケーションコードのコピー
# ----------------------------------------------------
# worker フォルダ全体を作業ディレクトリにコピー
# これには celery_app.py, repository/, tasks/ など全てが含まれます
COPY . /app/worker/

# ----------------------------------------------------
# 3. 起動コマンド (CMD は docker-compose.yml で上書きされるため、ここでは省略可能ですが、
#    ここでは Celery の実行環境を想定したコマンドを記述します)
# ----------------------------------------------------
# Celeryは docker-compose.yml の command で実行されるため、ここでは定義しません。
# CMD ["celery", "-A", "worker.celery_app", "worker", "-l", "info"]