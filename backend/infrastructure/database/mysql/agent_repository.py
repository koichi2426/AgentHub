import mysql.connector
from mysql.connector import pooling
from typing import Optional, List
from contextlib import contextmanager

from domain.entities.agent import Agent, NewAgent, AgentRepository
from domain.value_objects.id import ID
from .config import MySQLConfig


class MySQLAgentRepository(AgentRepository):
    """
    AgentRepository の MySQL 実装
    """

    def __init__(self, config: MySQLConfig):
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="agent_repo_pool",
                pool_size=5,
                pool_reset_session=True,
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database=config.database
            )
        except mysql.connector.Error as err:
            print(f"Error initializing agent connection pool: {err}")
            raise

    @contextmanager
    def _get_cursor(self, commit: bool = False):
        """
        コネクションプールからカーソルを取得し、処理後にクローズするコンテキストマネージャ
        """
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
            print(f"Database error in agent repository: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _map_row_to_agent(self, row: tuple) -> Optional[Agent]:
        """
        DBから取得した単一の行(タプル)をAgentドメインオブジェクトに変換する
        """
        if not row:
            return None
        
        # (id, user_id, owner, name, description) の順序を想定
        return NewAgent(
            id=row[0],
            user_id=row[1],
            owner=row[2],
            name=row[3],
            description=row[4]
        )

    def create(self, agent: Agent) -> Agent:
        sql = """
        INSERT INTO agents (user_id, owner, name, description)
        VALUES (%s, %s, %s, %s)
        """
        data = (
            agent.user_id.value,
            agent.owner,
            agent.name,
            agent.description
        )

        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            new_id = cursor.lastrowid

        # 新しく採番されたIDでAgentオブジェクトを再構築して返す
        return NewAgent(
            id=new_id,
            user_id=agent.user_id.value,
            owner=agent.owner,
            name=agent.name,
            description=agent.description
        )

    def find_by_id(self, agent_id: "ID") -> Optional[Agent]:
        sql = "SELECT id, user_id, owner, name, description FROM agents WHERE id = %s"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (agent_id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_agent(row)

    def list_by_user_id(self, user_id: "ID") -> List[Agent]:
        sql = "SELECT id, user_id, owner, name, description FROM agents WHERE user_id = %s ORDER BY id"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (user_id.value,))
            rows = cursor.fetchall()
            
        return [self._map_row_to_agent(row) for row in rows if row]

    def find_all(self) -> List[Agent]:
        sql = "SELECT id, user_id, owner, name, description FROM agents ORDER BY id"
        with self._get_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            
        return [self._map_row_to_agent(row) for row in rows if row]

    def update(self, agent: Agent) -> None:
        sql = """
        UPDATE agents
        SET name = %s, description = %s
        WHERE id = %s AND user_id = %s
        """
        data = (
            agent.name,
            agent.description,
            agent.id.value,
            agent.user_id.value
        )
        
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)

    def delete(self, agent_id: "ID") -> None:
        sql = "DELETE FROM agents WHERE id = %s"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, (agent_id.value,))

