# repository

このディレクトリは Repository 層を格納します。

目的:
- データストア（RDBMS、オブジェクトストレージ、外部 API など）へのアクセスを抽象化する責務を持ちます。
- SQL や ORM の細かい処理、トランザクション管理、永続化の詳細をここに閉じ込め、ユースケース層はインターフェースを通じて利用します。

例:
- `AgentRepository`（find_by_id, list_by_owner, create, update, delete）
- `FinetuningJobRepository`（create_job, list_jobs_by_agent, get_job, update_status）
- `DeploymentRepository`（create_deployment, get_by_model_id, delete_deployment）

実装ノート:
- SQLAlchemy のセッションや Alembic との連携はここで扱います。
- テストしやすくするためにインターフェース（抽象クラス）を定義し、実装は concrete adapter として分けます。
