# プロジェクトセットアップ手順

このドキュメントは、リポジトリをクローンしてから開発環境を完全にセットアップするまでの手順を説明します。

## 1\. 前提条件

以下のツールがあなたの開発マシンにインストールされている必要があります。

  * **Git:** ソースコードをダウンロードするために使用します。
  * **Docker:** コンテナを実行するために使用します。
  * **Docker Compose:** 複数のコンテナ（フロントエンド、バックエンド、DB）を管理するために使用します。

-----

## 2\. セットアップ手順

### ステップ1: リポジトリのクローン

まず、プロジェクトのソースコードをローカルマシンにダウンロードします。

```bash
git clone https://github.com/koichi2426/AgentHub.git
cd AgentHub
```

### ステップ2: 環境変数の設定

プロジェクトのルートディレクトリ（`docker-compose.yml`がある場所）に `.env` という名前のファイルを作成し、以下の内容をコピー＆ペーストしてください。このファイルは、Dockerコンテナが使用するデータベースのパスワードなどの重要な設定を管理します。

```dotenv
# データベース接続情報 (MySQL)
# FastAPIアプリとMySQLコンテナがこの設定を参照します

DB_USER=user
DB_PASSWORD=password
DB_ROOT_PASSWORD=rootpassword
DB_NAME=agenthub_db
DB_HOST=db
DB_PORT=3306

# FastAPIが直接参照するURL (主に参考用)
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

**【重要】**
`DB_HOST` は `db` のままにしてください。これはDockerネットワーク内でバックエンドコンテナがMySQLコンテナを見つけるための名前です。

### ステップ3: Dockerコンテナのビルドと起動

以下のコマンドを実行して、プロジェクトに必要なすべてのコンテナ（フロントエンド、バックエンド、データベース）をビルドし、バックグラウンドで起動します。

```bash
docker-compose up --build -d
```

  * `--build`: `Dockerfile`や`requirements.txt`に変更があった場合に、Dockerイメージを再構築します。初回起動時は必須です。
  * `-d`: コンテナをバックグラウンド（detachedモード）で起動します。

### ステップ4: データベースマイグレーションの実行

コンテナが起動したら、バックエンドコンテナの中に入って、データベースにテーブルを作成するコマンドを実行します。この作業は**Alembic**というツールで行います。

**【なぜコンテナ内で実行するのか？】**
`DB_HOST=db`という設定はDockerネットワークの内部でのみ有効です。そのため、`alembic`コマンドも`db`というホスト名を解決できるバックエンドコンテナの中から実行する必要があります。

1.  **マイグレーションスクリプトの作成**
    モデルの定義 (`models.py`) と現在のデータベースの状態を比較し、テーブルを作成するためのスクリプト（設計図）を自動生成します。

    ```bash
    docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
    ```

2.  **マイグレーションの適用**
    生成されたスクリプトを実行し、実際にデータベースにテーブルを作成します。

    ```bash
    docker-compose exec backend alembic upgrade head
    ```

### ステップ5: セットアップの確認

全てのステップが完了したら、アプリケーションが正常に動作しているか確認しましょう。

  * **フロントエンドの確認:**
    ブラウザで `http://localhost:3000` にアクセスします。Next.jsの画面が表示されれば成功です。

  * **バックエンドの確認:**
    ブラウザで `http://localhost:8000/docs` にアクセスします。FastAPIの自動生成APIドキュメント（Swagger UI）が表示されれば成功です。

  * **コンテナのログ確認:**
    もし何か問題が発生した場合は、以下のコマンドで各コンテナのログを確認できます。

    ```bash
    # すべてのログを表示
    docker-compose logs -f

    # バックエンドのログのみ表示
    docker-compose logs -f backend
    ```

-----

## 開発の停止

開発を終了する際は、以下のコマンドでコンテナを停止します。

```bash
docker-compose down
```

**【注意】**
データベースのデータを**完全に削除して**やり直したい場合のみ、以下のコマンドを実行してください。

```bash
docker-compose down -v
```

この場合、次回起動時に再度ステップ4のデータベースマイグレーションが必要になります。
