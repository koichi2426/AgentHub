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

# 必要なPythonパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------
# 🚨 GGUF 変換ツールのインストール (llama.cppに置き換え)
# ----------------------------------------------------
# C/C++プロジェクトのビルドに必要なツールとgit、およびCURLのライブラリをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        cmake \
        build-essential \
        libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/*

# 1. llama.cpp プロジェクト一式をコンテナ内の /app/llama.cpp にクローン
RUN git clone https://github.com/ggerganov/llama.cpp.git /app/llama.cpp

# 2. llama.cpp の Python 依存関係 (GGUF変換スクリプト用) をインストール
RUN pip install --no-cache-dir -r /app/llama.cpp/requirements.txt

# 3. llama.cpp をビルドし、実行可能ファイル (quantizeなど) を用意
#    cmake -B build: buildディレクトリを作成し、ビルドファイルを生成
#    cmake --build build: 実際のビルドを実行
#    -- -j$(nproc): コア数に応じた並列ビルド (高速化)
RUN cd /app/llama.cpp && cmake -B build && cmake --build build -- -j$(nproc)

# 4. train_and_export.py がスクリプトを見つけられるよう環境変数を設定
#    HuggingFace → GGUF F16 変換用スクリプト
ENV GGUF_CONVERT_SCRIPT=/app/llama.cpp/convert_hf_to_gguf.py

#    GGUF F16 → GGUF Q4_0 量子化用バイナリ
ENV GGUF_QUANTIZE_SCRIPT=/app/llama.cpp/build/bin/quantize
# ----------------------------------------------------
# 置き換え完了
# ----------------------------------------------------


# ----------------------------------------------------
# 2. アプリケーションコードのコピー
# ----------------------------------------------------
# worker フォルダ全体を作業ディレクトリにコピー
# これには celery_app.py, repository/, tasks/ など全てが含まれます
COPY . /app/worker/

# ----------------------------------------------------
# 3. 起動コマンド
# ----------------------------------------------------
# Celeryは docker-compose.yml の command で実行されるため、ここでは定義しません。
# CMD ["celery", "-A", "worker.celery_app", "worker", "-l", "info"]
