import abc
from typing import List

# ユースケース層の依存関係（Output DTOとPresenterインターフェース）
from usecase.get_weight_visualizations import (
    GetFinetuningJobVisualizationPresenter, 
    GetFinetuningJobVisualizationOutput, 
    LayerVisualizationOutput,
    WeightVisualizationDetail
)
# ドメイン層の依存関係（エンティティと値オブジェクト）
from domain.entities.weight_visualization import WeightVisualization
from domain.value_objects.visualization_details import LayerVisualization, WeightDetail


class GetFinetuningJobVisualizationPresenterImpl(GetFinetuningJobVisualizationPresenter):
    def output(self, visualization: WeightVisualization) -> GetFinetuningJobVisualizationOutput:
        """
        WeightVisualizationエンティティをOutput DTOに変換して返す。
        """
        
        # 1. LayerVisualization (VO) のリストを LayerVisualizationOutput (DTO) のリストに変換
        layers_output: List[LayerVisualizationOutput] = []
        
        for layer_vo in visualization.layers:
            # 2. WeightDetail (VO) のリストを WeightVisualizationDetail (DTO) に変換
            weights_output: List[WeightVisualizationDetail] = []
            for weight_vo in layer_vo.weights:
                weights_output.append(
                    WeightVisualizationDetail(
                        name=weight_vo.name,
                        before_url=weight_vo.before_url,
                        after_url=weight_vo.after_url,
                        delta_url=weight_vo.delta_url,
                    )
                )
            
            layers_output.append(
                LayerVisualizationOutput(
                    layer_name=layer_vo.layer_name,
                    weights=weights_output
                )
            )

        # 3. 最終的な Output DTO に格納して返す
        return GetFinetuningJobVisualizationOutput(
            job_id=visualization.job_id.value,
            layers=layers_output
        )


def new_get_finetuning_job_visualization_presenter() -> GetFinetuningJobVisualizationPresenter:
    """
    GetFinetuningJobVisualizationPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetFinetuningJobVisualizationPresenterImpl()
