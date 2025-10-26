import abc
from dataclasses import dataclass, field
from typing import List, Optional, Any

# 依存関係
from domain.value_objects.id import ID
from domain.value_objects.visualization_details import LayerVisualization, WeightDetail # 作成した値オブジェクトをインポート

@dataclass
class WeightVisualization:
    """特定のジョブに紐づく重みの可視化情報全体を表すエンティティ。"""
    job_id: ID # 関連する FinetuningJob の ID
    layers: List[LayerVisualization] = field(default_factory=list)


class WeightVisualizationRepository(abc.ABC):
    """WeightVisualizationエンティティの永続化を抽象化するリポジトリインターフェース (CRUD)。"""
    @abc.abstractmethod
    def save(self, visualization: "WeightVisualization") -> "WeightVisualization":
        """可視化データを新規保存または更新する (Create / Update)。"""
        pass

    @abc.abstractmethod
    def find_by_job_id(self, job_id: ID) -> Optional["WeightVisualization"]:
        """ジョブIDから可視化データを取得する (Read)。"""
        pass

    @abc.abstractmethod
    def delete_by_job_id(self, job_id: ID) -> None:
        """ジョブIDに紐づく可視化データを削除する (Delete)。"""
        pass


def NewWeightVisualization(
    job_id: int,
    layers_data: List[dict] # JSON構造に近い辞書のリスト
) -> WeightVisualization:
    """
    WeightVisualizationエンティティを生成するファクトリ関数。
    入力データから値オブジェクトへの変換を行う。
    """
    
    layers = []
    for layer_dict in layers_data:
        weights = []
        for weight_dict in layer_dict.get("weights", []):
            # WeightDetail 値オブジェクトを作成 (キーが存在しない場合のフォールバックを空文字列に)
            weight_detail = WeightDetail(
                name=weight_dict.get("name", ""),
                before_url=weight_dict.get("before_url", ""),
                after_url=weight_dict.get("after_url", ""),
                delta_url=weight_dict.get("delta_url", "")
            )
            weights.append(weight_detail)
        
        # LayerVisualization 値オブジェクトを作成
        layer_vis = LayerVisualization(
            layer_name=layer_dict.get("layer_name", ""),
            weights=weights
        )
        layers.append(layer_vis)

    return WeightVisualization(
        job_id=ID(job_id),
        layers=layers
    )
