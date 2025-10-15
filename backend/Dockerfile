# Pythonの公式軽量イメージを使用
FROM python:3.10-slim

# 作業ディレクトリを設定
WORKDIR /app

# 環境変数を設定（UTF-8対応）
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 依存ライブラリのリストをコピー
COPY requirements.txt .

# 依存ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# コンテナ起動時にAPIサーバーを実行（0.0.0.0を指定）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
