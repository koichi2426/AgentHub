import mysql.connector
from mysql.connector import pooling
from typing import Optional, List, Any, Dict
from contextlib import contextmanager

# ドメインエンティティのインポート
from domain.entities.deployment import (
    Deployment,
    DeploymentRepository,
)
from domain.value_objects.id import ID

# インフラストラクチャ層の依存関係
from .config import MySQLConfig


class MySQLDeploymentRepository(DeploymentRepository):

    def __init__(self, config: MySQLConfig):
        try:
            # 接続プールの初期化 (プール名を変更)
            self.pool = pooling.MySQLConnectionPool(
                pool_name="deployment_repo_pool",
                pool_size=5,
                pool_reset_session=True,
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database=config.database
            )
        except mysql.connector.Error as err:
            print(f"Error initializing connection pool: {err}")
            raise

    @contextmanager
    def _get_cursor(self, commit: bool = False):
        """データベース接続とカーソルを管理するコンテキストマネージャ"""
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _map_row_to_deployment(self, row: tuple) -> Optional[Deployment]:
        """データベースの行データを Deployment エンティティにマッピング"""
        if not row:
            return None
        
        # NOTE: rowのインデックスは SQL の SELECT 順序に依存します
        # 0: id, 1: job_id, 2: status, 3: endpoint
        
        return Deployment(
            id=ID(row[0]),
            job_id=ID(row[1]),
            status=row[2],
            endpoint=row[3]
        )

    def create(self, deployment: Deployment) -> Deployment:
        """
        デプロイメントを作成して返す
        """
        sql = """
        INSERT INTO deployments 
        (job_id, status, endpoint)
        VALUES (%s, %s, %s)
        """
        data = (
            deployment.job_id.value,
            deployment.status,
            deployment.endpoint
        )

        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            new_id = cursor.lastrowid
        
        # DBで生成されたIDを反映して返す
        return Deployment(
            id=ID(new_id),
            job_id=deployment.job_id,
            status=deployment.status,
            endpoint=deployment.endpoint
        )

    def find_by_id(self, deployment_id: "ID") -> Optional[Deployment]:
        """
        IDからデプロイメントを取得する
        """
        sql = """
        SELECT id, job_id, status, endpoint
        FROM deployments WHERE id = %s
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql, (deployment_id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_deployment(row)

    def list_by_agent(self, agent_id: "ID") -> list[Deployment]:
        """
        指定エージェントに関連するデプロイメント一覧を取得する
        (finetuning_jobs テーブルとJOINして agent_id を参照)
        """
        sql = """
        SELECT
            d.id, d.job_id, d.status, d.endpoint
        FROM deployments d
        JOIN finetuning_jobs fj ON d.job_id = fj.id
        WHERE fj.agent_id = %s
        ORDER BY d.id DESC
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql, (agent_id.value,))
            rows = cursor.fetchall()
            
        return [self._map_row_to_deployment(row) for row in rows if row]

    def find_by_job_id(self, job_id: "ID") -> Optional[Deployment]:
        """
        job_id に紐づくデプロイメントを（1件）検索する
        """
        sql = """
        SELECT id, job_id, status, endpoint
        FROM deployments WHERE job_id = %s
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql, (job_id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_deployment(row)

    def delete(self, deployment_id: "ID") -> None:
        """
        デプロイメントを削除する
        """
        sql = "DELETE FROM deployments WHERE id = %s"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, (deployment_id.value,))

    # -----------------------------------------------------------------
    # NOTE: DeploymentRepository ABC には 'update' が定義されていません。
    # もしステータス更新などが必要な場合は、ABCとこの実装に 'update' メソッドを追加する必要があります。
    # -----------------------------------------------------------------