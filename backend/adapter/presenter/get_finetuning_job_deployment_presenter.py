# ★ 参照するユースケースとDTOを 'GetFinetuningJobDeployment' のものに変更
from usecase.get_finetuning_job_deployment import (
    GetFinetuningJobDeploymentPresenter,
    GetFinetuningJobDeploymentOutput,
)
# ドメインエンティティをインポート
from domain.entities.deployment import Deployment


class GetFinetuningJobDeploymentPresenterImpl(GetFinetuningJobDeploymentPresenter):
    def output(self, deployment: Deployment) -> GetFinetuningJobDeploymentOutput:
        """
        Deploymentドメインオブジェクトを GetFinetuningJobDeploymentOutput DTO に変換して返す。
        """
        # DeploymentエンティティのフィールドをDTOにマッピング
        return GetFinetuningJobDeploymentOutput(
            id=deployment.id.value,
            finetuning_job_id=deployment.job_id.value,
            status=deployment.status,
            endpoint=deployment.endpoint,
        )


def new_get_finetuning_job_deployment_presenter() -> GetFinetuningJobDeploymentPresenter:
    """
    GetFinetuningJobDeploymentPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetFinetuningJobDeploymentPresenterImpl()