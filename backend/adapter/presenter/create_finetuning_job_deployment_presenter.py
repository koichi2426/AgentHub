from usecase.create_finetuning_job_deployment import CreateFinetuningJobDeploymentPresenter, CreateFinetuningJobDeploymentOutput
from domain.entities.deployment import Deployment


class CreateFinetuningJobDeploymentPresenterImpl(CreateFinetuningJobDeploymentPresenter):
    def output(self, deployment: Deployment) -> CreateFinetuningJobDeploymentOutput:
        """
        Deploymentドメインオブジェクトを CreateFinetuningJobDeploymentOutput DTO に変換して返す。
        """
        return CreateFinetuningJobDeploymentOutput(
            id=deployment.id.value,
            finetuning_job_id=deployment.job_id.value,
            status=deployment.status,
            endpoint=deployment.endpoint,
        )


def new_create_finetuning_job_deployment_presenter() -> CreateFinetuningJobDeploymentPresenter:
    """
    CreateFinetuningJobDeploymentPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return CreateFinetuningJobDeploymentPresenterImpl()