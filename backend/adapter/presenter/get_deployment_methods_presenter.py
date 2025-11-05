from typing import List

from usecase.get_deployment_methods import (
    GetDeploymentMethodsPresenter,
    GetDeploymentMethodsOutput,
    MethodListItemDTO, # ★ Output DTOの内部DTOをインポート
)


class GetDeploymentMethodsPresenterImpl(GetDeploymentMethodsPresenter):
    # ユースケースからの出力が List[Method] (Value Object) だと仮定して修正
    def output(self, method_vos: List[str]) -> GetDeploymentMethodsOutput:
        """
        メソッドの文字列リスト（Value Object）を GetDeploymentMethodsOutput DTO に変換して返す。
        """
        
        # Value Object (Method) が持つメソッド名（文字列）を取得し、DTOに変換
        method_list_dtos: List[MethodListItemDTO] = [
            MethodListItemDTO(name=method_vo.name) 
            for method_vo in method_vos # 引数名を method_vos に変更
        ]

        # GetDeploymentMethodsOutput は deployment_id を持たないと仮定し、methodsのみを返す
        return GetDeploymentMethodsOutput(
            methods=method_list_dtos
        )


def new_get_deployment_methods_presenter() -> GetDeploymentMethodsPresenter:
    """
    GetDeploymentMethodsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetDeploymentMethodsPresenterImpl()