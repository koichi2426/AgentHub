from typing import List

# ★ 参照するユースケースとDTOを 'SetDeploymentMethods' のものに変更
from usecase.set_deployment_methods import (
    SetDeploymentMethodsPresenter,
    SetDeploymentMethodsOutput,
)


class SetDeploymentMethodsPresenterImpl(SetDeploymentMethodsPresenter):
    def output(self, methods: List[str]) -> SetDeploymentMethodsOutput:
        """
        設定されたメソッドの文字列リストを SetDeploymentMethodsOutput DTO に変換して返す。
        """
        # SetDeploymentMethodsOutput DTO が 'methods' フィールドを持つと仮定
        return SetDeploymentMethodsOutput(
            methods=methods
        )


def new_set_deployment_methods_presenter() -> SetDeploymentMethodsPresenter:
    """
    SetDeploymentMethodsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return SetDeploymentMethodsPresenterImpl()