from typing import List

# ★ 参照するユースケースとDTOを 'SetDeploymentMethods' のものに変更
from usecase.set_deployment_methods import (
    SetDeploymentMethodsPresenter,
    SetDeploymentMethodsOutput,
    MethodListItemDTO, # ★ Outputを構築するために、内部DTOをインポート
)
# ★★★ 修正箇所1: ユースケースから渡されるエンティティをインポート ★★★
from domain.entities.methods import DeploymentMethods


class SetDeploymentMethodsPresenterImpl(SetDeploymentMethodsPresenter):
    # 修正2: 引数を List[str] ではなく、DeploymentMethods エンティティに変更
    def output(self, methods_entity: DeploymentMethods) -> SetDeploymentMethodsOutput:
        """
        設定されたメソッドのエンティティを SetDeploymentMethodsOutput DTO に変換して返す。
        """
        # ★★★ 修正3: deployment_id と methods リストを構築 ★★★
        
        # DeploymentMethods.methods は List[Method] (Value Object) なので、
        # Output DTOの List[MethodListItemDTO] に変換
        method_list_dtos: List[MethodListItemDTO] = [
            # ⬇️⬇️⬇️ 修正: .value を .name に変更 ⬇️⬇️⬇️
            MethodListItemDTO(name=method_vo.name) 
            # ⬆️⬆️⬆️ 修正: .value を .name に変更 ⬆️⬆️⬆️
            for method_vo in methods_entity.methods
        ]
        
        return SetDeploymentMethodsOutput(
            # DeploymentIDエンティティから値(.value)を取り出すと仮定
            deployment_id=methods_entity.deployment_id.value, 
            methods=method_list_dtos
        )


def new_set_deployment_methods_presenter() -> SetDeploymentMethodsPresenter:
    """
    SetDeploymentMethodsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return SetDeploymentMethodsPresenterImpl()