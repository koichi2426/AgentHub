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
# データベース接続情報 (MySQL)
DB_USER=user
DB_PASSWORD=password
DB_ROOT_PASSWORD=rootpassword
DB_NAME=agenthub_db
DB_HOST=db
DB_PORT=3306

DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
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
