from typing import List

from usecase.set_deployment_methods import (
    SetDeploymentMethodsPresenter,
    SetDeploymentMethodsOutput,
    MethodListItemDTO,
)
from domain.entities.methods import DeploymentMethods


class SetDeploymentMethodsPresenterImpl(SetDeploymentMethodsPresenter):
    def output(self, methods_entity: DeploymentMethods) -> SetDeploymentMethodsOutput:
        """
        設定されたメソッドのエンティティを SetDeploymentMethodsOutput DTO に変換して返す。
        """
        
        # DeploymentMethods.methods は List[Method] (Value Object) なので、
        # Output DTOの List[MethodListItemDTO] に変換
        method_list_dtos: List[MethodListItemDTO] = [
            MethodListItemDTO(name=method_vo.name) 
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