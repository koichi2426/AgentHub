# AgentHub プロジェクトセットアップ手順

本記事では、**AgentHub** プロジェクトの開発環境構築から起動までの手順を詳しく説明します。  
Dockerを用いたフルスタック構成（FastAPI + Next.js + MySQL + Redis + Celery）です。

---

## 1. 必要なツール

事前に以下のツールをインストールしてください。

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 2. セットアップ手順

### ステップ1: リポジトリのクローン

```bash
git clone https://github.com/koichi2426/AgentHub.git
cd AgentHub
```

---

### ステップ2: 環境変数 (.env) の設定

プロジェクトルートに `.env` ファイルを作成しください。  

### ステップ3: VPS秘密鍵パス (`VPS_KEY_HOST_PATH`) の設定

`.env` ファイルの `VPS_KEY_HOST_PATH`（ホストPC上の秘密鍵のパス）を設定するため、  
以下の手順でVPS接続用の秘密鍵を特定・準備します。

---

#### 1. VPSへの手動接続確認

まず、あなたのPCからVPSにSSH接続できるか確認します。

```bash
ssh [VPS_USER]@[VPS_IP]
```

例：

```bash
ssh ubuntu@your-vps-address
```

> `.env` に設定した `VPS_IP` と `VPS_USER` を使用してください。  
> 接続時に `VPS_ACCOUNT_PASSWORD` の入力を求められる場合があります。

---

#### 2. 使用する秘密鍵の特定

SSH接続で使用される（または使用予定の）秘密鍵ファイルを確認します。  
通常は `~/.ssh/` ディレクトリに存在します。

```bash
ls -l ~/.ssh
```

---

#### 3. 鍵の形式を確認

秘密鍵の1行目を確認して形式を判定します。

```bash
head -n 1 [秘密鍵のパス]
```

---

#### 4. 鍵の変換（必要な場合）

##### 4-1. もし1行目が

```
-----BEGIN OPENSSH PRIVATE KEY-----
```

の場合：  
Pythonの`Paramiko`では扱えない新形式です。以下の手順で古いPEM形式に変換してください。

```bash
# 1. コピーを作成（元の鍵は変更しない）
cp [元の鍵パス] [元の鍵パス]_legacy_pem

# 2. PEM形式に変換
ssh-keygen -p -m PEM -f [元の鍵パス]_legacy_pem -N ""
```

変換後、`.env` の `VPS_KEY_HOST_PATH` に以下のように設定します：

```
VPS_KEY_HOST_PATH=/Users/あなたのユーザー名/.ssh/id_rsa_legacy_pem
```

---

##### 4-2. もし1行目が

```
-----BEGIN RSA PRIVATE KEY-----
```

の場合：  
古い形式のため変換不要です。`.env` には元の鍵パスを設定します。

```
VPS_KEY_HOST_PATH=/Users/あなたのユーザー名/.ssh/id_rsa
```

---

#### 5. `.env` の更新

上記手順で確定した秘密鍵パスを `.env` の `VPS_KEY_HOST_PATH` に反映してください。

---

### ステップ4: Dockerコンテナの起動

以下のコマンドでコンテナをビルド・起動します。

```bash
docker-compose up --build -d
```

オプションの意味：

* `--build`: 初回起動時やDockerfileを変更した際に必須  
* `-d`: バックグラウンドで実行

---

### ステップ5: データベースマイグレーション（Alembic）

コンテナ起動後、FastAPIコンテナ内でAlembicを実行しテーブルを作成します。

> `DB_HOST=db` はコンテナ内限定のホスト名のため、**必ずコンテナ内で実行**します。

#### 1. マイグレーションスクリプトの自動生成

```bash
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
```

#### 2. マイグレーションの適用（テーブル作成）

```bash
docker-compose exec backend alembic upgrade head
```

---

### ステップ6: 動作確認

以下のURLにアクセスして、各サービスが正しく動作していることを確認します。

| サービス | URL |
|-----------|-----|
| フロントエンド | [http://localhost:3000](http://localhost:3000) |
| バックエンド(API Docs) | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

#### ログ確認（トラブルシューティング）

```bash
# 全ログをリアルタイムで確認
docker-compose logs -f

# バックエンドのみ
docker-compose logs -f backend
```

---

### ステップ7: 開発環境の停止とクリーンアップ

#### コンテナ停止

```bash
docker-compose down
```

#### データベース含めて完全削除（注意）

> **この操作はDBデータを完全に削除します。**  
> 必要に応じて実行してください。

```bash
docker-compose down -v
```

削除後に再起動する際は、**再度ステップ5のマイグレーション**を行う必要があります。

---

## まとめ

| ステップ | 内容 |
|----------|------|
| 1 | リポジトリのクローン |
| 2 | `.env` 設定 |
| 3 | VPS秘密鍵の登録 |
| 4 | Dockerコンテナ起動 |
| 5 | Alembicマイグレーション |
| 6 | 動作確認 |
| 7 | 停止・削除 |

---

### 補足

- `.env` の管理を一元化することで Docker Secrets を不要化  
- Paramiko対応のPEM形式鍵を使用  
- 開発・本番を同構成で再現可能な設計  

---

以上でセットアップ完了です。  
これで AgentHub プロジェクトをローカル環境で実行できます。

### アーキテクチャ
<img width="16384" height="7457" alt="image" src="https://github.com/user-attachments/assets/dfede11e-7402-438e-98c7-610b2e7710b9" />
