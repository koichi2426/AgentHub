import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class WeightVisualization:
    name: str
    before: str
    after: str
    delta: str


@dataclass
class WeightLayer:
    layer_name: str
    weights: list[WeightVisualization]


@dataclass
class Visualizations:
    job_id: str
    layers: list[WeightLayer]


class WeightVisualizationRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, visualizations: Visualizations) -> Visualizations:
        """
        重み可視化データを保存して返す
        """
        pass

    @abc.abstractmethod
    def find_by_job(self, job_id: "ID") -> Optional[Visualizations]:
        """
        ジョブIDから可視化データを取得する
        """
        pass


def NewWeightVisualization(
    job_id: int,
    layers: list,
) -> "WeightVisualization":
    return WeightVisualization(job_id=ID(job_id), layers=layers)
