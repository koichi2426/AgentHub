import abc
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass(frozen=True) # 値オブジェクトは不変
class WeightDetail:
    """単一の重みに関する可視化詳細（画像URL）"""
    name: str
    before_url: str
    after_url: str
    delta_url: str

@dataclass(frozen=True) # 値オブジェクトは不変
class LayerVisualization:
    """単一のレイヤーに関する可視化情報"""
    layer_name: str
    weights: List[WeightDetail]
