from usecase.create_finetuning_job_deployment import (
    CreateFinetuningJobDeploymentPresenter, 
    CreateFinetuningJobDeploymentOutput,
    # ★ 修正1: 内部のDTOをインポートに追加 ★
    CreatedDeploymentDTO 
)
from domain.entities.deployment import Deployment


class CreateFinetuningJobDeploymentPresenterImpl(CreateFinetuningJobDeploymentPresenter):
    def output(self, deployment: Deployment) -> CreateFinetuningJobDeploymentOutput:
        """
        Deploymentドメインオブジェクトを CreateFinetuningJobDeploymentOutput DTO に変換して返す。
        """
        
        # 1. 内部の CreatedDeploymentDTO を作成
        internal_dto = CreatedDeploymentDTO(
            id=deployment.id.value,
            job_id=deployment.job_id.value,
            status=deployment.status,
            endpoint=deployment.endpoint,
        )
        
        # 2. ★ 修正2: DTOを 'deployment' キーでラップして返す ★
        return CreateFinetuningJobDeploymentOutput(
            deployment=internal_dto
        )


def new_create_finetuning_job_deployment_presenter() -> CreateFinetuningJobDeploymentPresenter:
    """
    CreateFinetuningJobDeploymentPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return CreateFinetuningJobDeploymentPresenterImpl()