import mysql.connector
import json
from mysql.connector import pooling
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# ドメインエンティティ/VOのインポート
from domain.entities.weight_visualization import WeightVisualization, WeightVisualizationRepository
from domain.value_objects.id import ID
from domain.value_objects.visualization_details import LayerVisualization, WeightDetail

# インフラストラクチャ層の依存関係
from .config import MySQLConfig


class MySQLWeightVisualizationRepository(WeightVisualizationRepository):
    """
    WeightVisualizationエンティティのMySQL永続化を担当するリポジトリ実装。
    ネストされたVOはJSONとして保存する。
    """

    def __init__(self, config: MySQLConfig):
        try:
            # 接続プールの初期化
            self.pool = pooling.MySQLConnectionPool(
                pool_name="vis_repo_pool",
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
        """DBカーソルを取得・管理するコンテキストマネージャ"""
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            # dictionary=True を使わないことで、User Repository との互換性を保つ（今回はタプルで処理）
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            print(f"Database error: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # --- ヘルパー関数 ---

    def _serialize_layers(self, layers: List[LayerVisualization]) -> str:
        """LayerVisualizationのリストをJSON文字列に変換"""
        layers_data = []
        for layer in layers:
            weights_data = [w.__dict__ for w in layer.weights] # WeightDetail (frozen=True) を辞書に変換
            layers_data.append({"layer_name": layer.layer_name, "weights": weights_data})
        return json.dumps(layers_data)

    def _deserialize_layers(self, layers_json_str: str) -> List[LayerVisualization]:
        """JSON文字列をLayerVisualizationのリストに変換"""
        layers = []
        if not layers_json_str:
            return layers
            
        try:
            layers_data = json.loads(layers_json_str)
            for layer_dict in layers_data:
                weights = []
                for weight_dict in layer_dict.get("weights", []):
                    # WeightDetail 値オブジェクトを再構築
                    weights.append(WeightDetail(
                        name=weight_dict.get("name", ""),
                        before_url=weight_dict.get("before_url", ""),
                        after_url=weight_dict.get("after_url", ""),
                        delta_url=weight_dict.get("delta_url", "")
                    ))
                layers.append(LayerVisualization(
                    layer_name=layer_dict.get("layer_name", ""),
                    weights=weights
                ))
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to deserialize layers data: {e}")
        except Exception as e:
            print(f"ERROR: Failed to map visualization data to VOs: {e}")
            
        return layers

    def _map_row_to_visualization(self, row: tuple) -> Optional[WeightVisualization]:
        """データベースの行データ (job_id, layers_data) をエンティティにマッピング"""
        if not row:
            return None
        
        # NOTE: row[0]: job_id (int), row[1]: layers_data (str/JSON)
        job_id_val = row[0]
        layers_json_str = row[1]

        layers = self._deserialize_layers(layers_json_str)
        
        return WeightVisualization(
            job_id=ID(job_id_val),
            layers=layers
        )

    # --- CRUD 実装 ---

    def save(self, visualization: WeightVisualization) -> WeightVisualization:
        """可視化データを新規保存または更新する (Create / Update)"""
        sql = """
        INSERT INTO weight_visualizations (job_id, layers_data)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE layers_data = VALUES(layers_data)
        """
        
        layers_json = self._serialize_layers(visualization.layers)
        data = (visualization.job_id.value, layers_json)

        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            
        return visualization # IDは既に持っているのでそのまま返す

    def find_by_job_id(self, job_id: ID) -> Optional[WeightVisualization]:
        """ジョブIDから可視化データを取得する (Read)"""
        sql = "SELECT job_id, layers_data FROM weight_visualizations WHERE job_id = %s"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (job_id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_visualization(row)

    def delete_by_job_id(self, job_id: ID) -> None:
        """ジョブIDに紐づく可視化データを削除する (Delete)"""
        sql = "DELETE FROM weight_visualizations WHERE job_id = %s"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, (job_id.value,))
