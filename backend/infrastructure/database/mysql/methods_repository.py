import mysql.connector
from mysql.connector import pooling
from typing import Optional, List, Any, Dict
from contextlib import contextmanager
import json # JSONシリアライズのために追加

# ドメインエンティティのインポート
from domain.entities.methods import (
    DeploymentMethods,
    DeploymentMethodsRepository,
    Method,
)
from domain.value_objects.id import ID

# インフラストラクチャ層の依存関係
from .config import MySQLConfig


class MySQLMethodsRepository(DeploymentMethodsRepository):
    """
    DeploymentMethodsRepository の MySQL 実装。
    メソッドのリストは JSON カラムに保存されることを前提とします。
    """

    def __init__(self, config: MySQLConfig):
        try:
            # 接続プールの初期化 (プール名を変更)
            self.pool = pooling.MySQLConnectionPool(
                pool_name="methods_repo_pool",
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

    def _map_row_to_deployment_methods(self, row: tuple) -> Optional[DeploymentMethods]:
        """データベースの行データを DeploymentMethods エンティティにマッピング"""
        if not row:
            return None
        
        # NOTE: rowのインデックスは SQL の SELECT 順序に依存します
        # 0: id, 1: deployment_id, 2: methods (JSON string)
        
        try:
            # JSON文字列をパースして文字列のリストを取得
            method_names = json.loads(row[2])
            # 文字列のリストを Method 値オブジェクトのリストに変換
            method_vos = [Method(name=name) for name in method_names if name]
        except (json.JSONDecodeError, TypeError):
            method_vos = [] # パース失敗時は空リスト
        
        return DeploymentMethods(
            id=ID(row[0]),
            deployment_id=ID(row[1]),
            methods=method_vos
        )

    def find_by_deployment_id(self, deployment_id: ID) -> Optional[DeploymentMethods]:
        """
        デプロイメントIDからメソッドの集合を取得する
        """
        sql = """
        SELECT id, deployment_id, methods
        FROM deployment_methods 
        WHERE deployment_id = %s
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql, (deployment_id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_deployment_methods(row)
    
    def find_by_id(self, id: ID) -> Optional[DeploymentMethods]:
        """
        このエンティティ自体のIDから取得する
        """
        sql = """
        SELECT id, deployment_id, methods
        FROM deployment_methods 
        WHERE id = %s
        """
        with self._get_cursor() as cursor:
            cursor.execute(sql, (id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_deployment_methods(row)

    def save(self, deployment_methods: DeploymentMethods) -> DeploymentMethods:
        """
        メソッドの集合を保存（作成または更新）する。
        deployment_id をキーとして Upsert を試みる。
        """
        
        # 1. エンティティからDB保存形式（JSON文字列）に変換
        method_names = deployment_methods.get_method_names()
        methods_json = json.dumps(method_names)
        deployment_id_val = deployment_methods.deployment_id.value

        # 2. 既にDBに存在するか (IDを知るため)
        existing = self.find_by_deployment_id(deployment_methods.deployment_id)
        
        if existing:
            # 3a. 存在する場合 (UPDATE)
            sql = """
            UPDATE deployment_methods 
            SET methods = %s
            WHERE id = %s
            """
            data = (methods_json, existing.id.value)
            with self._get_cursor(commit=True) as cursor:
                cursor.execute(sql, data)
            
            # 更新されたエンティティを返す (IDは既存のものを引き継ぐ)
            return DeploymentMethods(
                id=existing.id,
                deployment_id=deployment_methods.deployment_id,
                methods=deployment_methods.methods
            )
        else:
            # 3b. 存在しない場合 (INSERT)
            sql = """
            INSERT INTO deployment_methods (deployment_id, methods)
            VALUES (%s, %s)
            """
            data = (deployment_id_val, methods_json)
            with self._get_cursor(commit=True) as cursor:
                cursor.execute(sql, data)
                new_id = cursor.lastrowid
            
            # DBで採番されたIDを持つ新しいエンティティを返す
            return DeploymentMethods(
                id=ID(new_id),
                deployment_id=deployment_methods.deployment_id,
                methods=deployment_methods.methods
            )

    def delete_by_deployment_id(self, deployment_id: ID) -> None:
        """
        デプロイメントIDに紐づくメソッドの集合を削除する
        """
        sql = "DELETE FROM deployment_methods WHERE deployment_id = %s"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, (deployment_id.value,))