# worker/tasks/finetuning/db_helpers.py

import os
import json
import mysql.connector
from mysql.connector import pooling
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime as PythonDateTime
from dataclasses import dataclass

# === Configuration (Loaded directly) ===
try:
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_NAME = os.environ["DB_NAME"]
except KeyError as e:
    raise EnvironmentError(f"FATAL: Missing DB environment variable: {e}")

# === Local Data Structure ===
@dataclass
class JobInfo:
    """Simplified local representation of job data needed by the worker."""
    id: int
    agent_id: int
    training_file_path: str
    status: str
    created_at: Optional[PythonDateTime] = None
    finished_at: Optional[PythonDateTime] = None
    error_message: Optional[str] = None

# === Database Connection Pool ===
db_pool = None

def _initialize_db_pool():
    global db_pool
    if db_pool is None:
        try:
            print("INFO: Initializing DB connection pool...")
            db_pool = pooling.MySQLConnectionPool(
                pool_name="executor_pool", pool_size=3, pool_reset_session=True,
                host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
            )
            print("INFO: DB connection pool initialized.")
        except mysql.connector.Error as err:
            print(f"FATAL: Failed to initialize DB pool: {err}")
            db_pool = None
            raise

@contextmanager
def get_db_cursor(commit: bool = False):
    """DBカーソルを取得・管理するコンテキストマネージャ"""
    if db_pool is None:
        _initialize_db_pool()
        if db_pool is None: raise ConnectionError("DB pool unavailable.")

    conn = None; cursor = None
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True) # Use dictionary cursor
        yield cursor
        if commit: conn.commit()
    except mysql.connector.Error as err:
        print(f"ERROR: DB operation failed: {err}")
        if conn: conn.rollback()
        raise
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# === Direct DB Operation Functions ===

def find_job_by_id(job_id: int) -> Optional[JobInfo]:
    """ジョブIDでジョブ情報をDBから取得"""
    sql = """
        SELECT id, agent_id, training_file_path, status, created_at, finished_at, error_message
        FROM finetuning_jobs WHERE id = %s
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (job_id,))
            row = cursor.fetchone()
        return JobInfo(**row) if row else None
    except Exception as e:
        print(f"ERROR: Job {job_id}: Failed to find job in DB: {e}")
        return None

def update_job_status(job_id: int, status: str,
                      finished_at: Optional[PythonDateTime] = None,
                      error_message: Optional[str] = None):
    """ジョブステータス等をDBで更新"""
    updates = {"status": status}
    if finished_at: updates["finished_at"] = finished_at
    if error_message is not None: updates["error_message"] = error_message[:1000] # Truncate

    set_clauses = [f"`{k}` = %s" for k in updates.keys()] # Backticks for safety
    data = list(updates.values())
    data.append(job_id)

    sql = f"UPDATE finetuning_jobs SET {', '.join(set_clauses)} WHERE id = %s"
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
        print(f"INFO: Job {job_id}: DB status updated to '{status}'.")
    except Exception as e:
        print(f"ERROR: Job {job_id}: CRITICAL - Failed to update final DB status: {e}")
        raise # Re-raise by default

def save_visualization(job_id: int, layers_data: List[Dict[str, Any]]):
    """可視化データをDBに保存"""
    sql = """
        INSERT INTO weight_visualizations (job_id, layers_data)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE layers_data = VALUES(layers_data)
    """
    try:
        layers_json = json.dumps(layers_data)
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (job_id, layers_json))
        print(f"INFO: Job {job_id}: Visualization data saved to DB.")
    except Exception as e:
        print(f"WARN: Job {job_id}: Failed to save visualization data to DB: {e}")

def close_db_pool():
    """アプリケーション終了時にDBプールを閉じる（オプション）"""
    global db_pool
    if db_pool:
        try:
            # Note: closeall() is not a standard method for mysql.connector.pooling
            # Connections are typically closed when returned to the pool via context manager
            print("INFO: DB connection pool cleanup (connections closed on release).")
            # If explicit closing is needed, manage connections individually
        except Exception as e:
            print(f"WARN: Error during DB pool cleanup: {e}")
        db_pool = None
