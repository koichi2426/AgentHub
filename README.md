# プロジェクトセットアップ手順

## 1\. 必要なツール

  * Git
  * Docker
  * Docker Compose

-----

## 2\. セットアップ

### ステップ1: リポジトリのクローン

```bash
git clone https://github.com/koichi2426/AgentHub.git
cd AgentHub
```

### ステップ2: 環境変数 (.env) の設定

プロジェクトルートに `.env` ファイルを作成し、以下をコピーします。

```dotenv
# ---------------------------------
# データベース接続情報 (MySQL)
# ---------------------------------
# これらの値は開発用です。本番環境ではより強力なパスワードに変更してください。
DB_USER=hoge
DB_PASSWORD=hoge
DB_ROOT_PASSWORD=hoge
DB_NAME=hoge
DB_HOST=hoge
DB_PORT=hoge

# FastAPIバックエンドが使用するデータベース接続URL
# 変数名をAlembicと統一
DATABASE_URL=hoge

# ---------------------------------
# JWT 設定
# ---------------------------------
SECRET_KEY=hoge
ALGORITHM=hoge
ACCESS_TOKEN_EXPIRE_MINUTES=hoge

# ---------------------------------
# Frontend (Next.js) 用
# ---------------------------------
# ブラウザからアクセスするAPIのURL
NEXT_PUBLIC_API_URL=hoge
# Next.jsサーバーからアクセスするAPIのURL (コンテナ間通信)
API_URL_INTERNAL=hoge

# ---------------------------------
# Celery/Redis 設定
# ---------------------------------
CELERY_BROKER_URL=hoge
CELERY_RESULT_BACKEND=hoge
CELERY_TASK_TIME_LIMIT=hoge
CELERY_TASK_MAX_RETRIES=hoge

# ---------------------------------
# SFTP Storage Settings
# ---------------------------------
# (ymlファイルからDocker Secretsの記述を削除し、こちらで一元管理します)
VPS_IP=hoge
VPS_USER=hoge
VPS_ACCOUNT_PASSWORD=hoge
VPS_KEY_HOST_PATH=hoge
VPS_KEY_FILE_PATH=hoge
```

**【重要】** `DB_HOST=db` は、Dockerネットワーク内のホスト名のため変更しないでください。

### ステップ3: Dockerコンテナの起動

コンテナをビルドしてバックグラウンドで起動します。

```bash
docker-compose up --build -d
```

  * `--build`: 初回起動時や`Dockerfile`変更時に必須。
  * `-d`: バックグラウンド実行。

### ステップ4: データベースマイグレーション (Alembic)

コンテナ起動後、コンテナ内でAlembicコマンドを実行しテーブルを作成します。
（**理由:** `DB_HOST=db` はコンテナ内でのみ有効なため）

1.  **マイグレーションスクリプトの自動生成:**
    ```bash
    docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
    ```
2.  **マイグレーションの適用 (テーブル作成):**
    ```bash
    docker-compose exec backend alembic upgrade head
    ```

### ステップ5: 動作確認

  * **フロントエンド:** `http://localhost:3000`
  * **バックエンド (API Docs):** `http://localhost:8000/docs`
  * **ログ確認 (問題発生時):**
    ```bash
    docker-compose logs -f
    docker-compose logs -f backend # バックエンドのみ
    ```

-----

## 3\. 開発の停止

### コンテナ停止

```bash
docker-compose down
```

### DBデータを含めた全削除

**【注意】** DBデータを完全に削除する場合のみ実行してください。

```bash
docker-compose down -v
```

（この場合、次回起動時にステップ4のマイグレーションが再度必要です）
