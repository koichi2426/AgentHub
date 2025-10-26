import mysql.connector
from mysql.connector import pooling
from typing import Optional, List, Any, Dict
from contextlib import contextmanager
from datetime import datetime

# ドメインエンティティのインポート
from domain.entities.finetuning_job import (
    FinetuningJob,
    FinetuningJobRepository,
)
from domain.value_objects.id import ID

# インフラストラクチャ層の依存関係
from .config import MySQLConfig


class MySQLFinetuningJobRepository(FinetuningJobRepository):

    def __init__(self, config: MySQLConfig):
        try:
            # 接続プールの初期化
            self.pool = pooling.MySQLConnectionPool(
                pool_name="finetuning_job_repo_pool",
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

    def _map_row_to_job(self, row: tuple) -> Optional[FinetuningJob]:
        """データベースの行データを FinetuningJob エンティティにマッピング"""
        if not row:
            return None
        
        # NOTE: rowのインデックスは SQL の SELECT 順序に依存します
        # 0: id, 1: agent_id, 2: training_file_path, 3: status,
        # 4: created_at, 5: finished_at, 6: error_message
        
        return FinetuningJob(
            id=ID(row[0]),
            agent_id=ID(row[1]),
            training_file_path=row[2],
            status=row[3],
            created_at=row[4],
            finished_at=row[5],
            error_message=row[6]
        )

    def create_job(self, job: FinetuningJob) -> FinetuningJob:
        sql = """
        INSERT INTO finetuning_jobs 
        (agent_id, training_file_path, status, created_at, finished_at, error_message)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = (
            job.agent_id.value,
            job.training_file_path,
            job.status,
            job.created_at,
            job.finished_at,
            job.error_message
        )

        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            new_id = cursor.lastrowid
        
        # DBで生成されたIDを反映して返す
        return FinetuningJob(
            id=ID(new_id),
            agent_id=job.agent_id,
            training_file_path=job.training_file_path,
            status=job.status,
            created_at=job.created_at,
            finished_at=job.finished_at,
            error_message=job.error_message
        )

    def find_by_id(self, job_id: "ID") -> Optional[FinetuningJob]:
        sql = """
        SELECT id, agent_id, training_file_path, status, created_at, finished_at, error_message
        FROM finetuning_jobs WHERE id = %s
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql, (job_id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_job(row)

    def is_any_running(self) -> bool:
        """status='running' のジョブがDBに存在するか確認する（ワーカー排他制御用）"""
        sql = "SELECT EXISTS(SELECT 1 FROM finetuning_jobs WHERE status = 'running' LIMIT 1)"
        with self._get_cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            return bool(result and result[0])

    def find_next_queued(self) -> Optional[FinetuningJob]:
        """最も古い 'queued' 状態のジョブを一つ取得する（ワーカーキュー処理用）"""
        sql = """
        SELECT id, agent_id, training_file_path, status, created_at, finished_at, error_message
        FROM finetuning_jobs 
        WHERE status = 'queued'
        ORDER BY created_at ASC
        LIMIT 1
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
        
        return self._map_row_to_job(row)

    def list_by_agent(self, agent_id: "ID") -> list[FinetuningJob]:
        """指定エージェントに紐づくジョブ一覧を取得する"""
        sql = """
        SELECT id, agent_id, training_file_path, status, created_at, finished_at, error_message
        FROM finetuning_jobs 
        WHERE agent_id = %s
        ORDER BY created_at DESC
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql, (agent_id.value,))
            rows = cursor.fetchall()
            
        return [self._map_row_to_job(row) for row in rows if row]

    def list_all_by_user(self, user_id: "ID") -> List[FinetuningJob]:
        """
        特定のユーザーが所有する全てのエージェントに紐づくジョブ一覧を取得する。
        """
        sql = """
        SELECT
            fj.id, fj.agent_id, fj.training_file_path, fj.status, fj.created_at, fj.finished_at, fj.error_message
        FROM finetuning_jobs fj
        JOIN agents a ON fj.agent_id = a.id
        WHERE a.user_id = %s
        ORDER BY fj.created_at DESC
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql, (user_id.value,))
            rows = cursor.fetchall()
        
        return [self._map_row_to_job(row) for row in rows if row]

    def update_job(self, job: FinetuningJob) -> FinetuningJob:
        """
        FinetuningJobエンティティの現在の状態に基づいてDBを更新する
        (インターフェースの update_job に合わせて実装)
        """
        sql = """
        UPDATE finetuning_jobs 
        SET 
            training_file_path = %s,
            status = %s,
            finished_at = %s,
            error_message = %s
        WHERE id = %s
        """
        data = (
            job.training_file_path,
            job.status,
            job.finished_at,
            job.error_message,
            job.id.value
        )
        
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            
        # 更新されたオブジェクトをそのまま返す
        return job

    def delete(self, job_id: "ID") -> None:
        sql = "DELETE FROM finetuning_jobs WHERE id = %s"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, (job_id.value,))

