from typing import List

# ★ 参照するユースケースとDTOを 'GetDeploymentMethods' のものに変更
from usecase.get_deployment_methods import (
    GetDeploymentMethodsPresenter,
    GetDeploymentMethodsOutput,
)


class GetDeploymentMethodsPresenterImpl(GetDeploymentMethodsPresenter):
    def output(self, methods: List[str]) -> GetDeploymentMethodsOutput:
        """
        メソッドの文字列リストを GetDeploymentMethodsOutput DTO に変換して返す。
        """
        # GetDeploymentMethodsOutput DTO が 'methods' フィールドを持つと仮定
        return GetDeploymentMethodsOutput(
            methods=methods
        )


def new_get_deployment_methods_presenter() -> GetDeploymentMethodsPresenter:
    """
    GetDeploymentMethodsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetDeploymentMethodsPresenterImpl()