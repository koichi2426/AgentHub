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


# ★★★ 新規追加: パス変換ヘルパー関数 ★★★
def _extract_relative_path(absolute_path: str) -> str:
    """
    VPSの絶対パスから、FastAPIプロキシ用の相対パスを抽出する。
    """
    # このベースパスは、VPS上の画像保存ルートディレクトリと一致している必要があります
    BASE_PATH = "/home/ubuntu/visualizations/"
    
    if absolute_path.startswith(BASE_PATH):
        # BASE_PATHの長さを使って、それ以降の相対パス部分を抽出
        return absolute_path[len(BASE_PATH):]
        
    # 予期せぬパス形式の場合、安全のためにそのまま返すか、エラーをログに記録すべき
    # 今回はそのまま返しますが、理想的にはこの時点でパス形式が統一されているべき
    return absolute_path


class GetFinetuningJobVisualizationPresenterImpl(GetFinetuningJobVisualizationPresenter):
    def output(self, visualization: WeightVisualization) -> GetFinetuningJobVisualizationOutput:
        """
        WeightVisualizationエンティティをOutput DTOに変換して返す。
        この際、URLをフロントエンドが直接使える相対パスに変換する。
        """
        
        # 1. LayerVisualization (VO) のリストを LayerVisualizationOutput (DTO) のリストに変換
        layers_output: List[LayerVisualizationOutput] = []
        
        for layer_vo in visualization.layers:
            # 2. WeightDetail (VO) のリストを WeightVisualizationDetail (DTO) に変換
            weights_output: List[WeightVisualizationDetail] = []
            for weight_vo in layer_vo.weights:
                
                # ★★★ 修正箇所: URLを変換してからDTOに格納する ★★★
                weights_output.append(
                    WeightVisualizationDetail(
                        name=weight_vo.name,
                        before_url=_extract_relative_path(weight_vo.before_url), # 変換
                        after_url=_extract_relative_path(weight_vo.after_url),   # 変換
                        delta_url=_extract_relative_path(weight_vo.delta_url),   # 変換
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