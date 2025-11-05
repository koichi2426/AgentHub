from typing import List

from usecase.get_deployment_methods import (
    GetDeploymentMethodsPresenter,
    GetDeploymentMethodsOutput,
    MethodListItemDTO, 
)

# ★★★ 修正箇所1: ユースケースから渡されるデータ型を明示的にインポートするか、定義する ★★★
# ここでは、ユースケースが deployment_id を直接渡すと仮定し、インターフェースを修正します。

class GetDeploymentMethodsPresenterImpl(GetDeploymentMethodsPresenter):
    # 修正: deployment_id を追加で受け取るようにする
    # ※ methods_vos は List[Method] (Value Object) だと仮定
    def output(self, deployment_id: int, method_vos: List) -> GetDeploymentMethodsOutput:
        """
        メソッド情報とデプロイメントIDを受け取り、Output DTOに変換して返す。
        """
        
        # Value Object (Method) が持つメソッド名（文字列）を取得し、DTOに変換
        method_list_dtos: List[MethodListItemDTO] = [
            MethodListItemDTO(name=method_vo.name) 
            for method_vo in method_vos
        ]

        # ★★★ 修正箇所2: deployment_id も含めて Output DTO を作成 ★★★
        return GetDeploymentMethodsOutput(
            deployment_id=deployment_id, # ← 追加！
            methods=method_list_dtos
        )


def new_get_deployment_methods_presenter() -> GetDeploymentMethodsPresenter:
    """
    GetDeploymentMethodsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetDeploymentMethodsPresenterImpl()