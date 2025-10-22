from usecase.create_finetuning_job import (
    CreateFinetuningJobPresenter,
    CreateFinetuningJobOutput,
)
from domain.entities.finetuning_job import FinetuningJob
from datetime import datetime # DTOの created_at の型注釈に必要


class CreateFinetuningJobPresenterImpl(CreateFinetuningJobPresenter):
    def output(self, job: FinetuningJob) -> CreateFinetuningJobOutput:
        """
        FinetuningJobドメインオブジェクトを CreateFinetuningJobOutput DTO に変換して返す。
        """
        # created_at は必ず存在するため、そのまま渡します
        created_at_dt: datetime = job.created_at

        return CreateFinetuningJobOutput(
            id=job.id.value,
            agent_id=job.agent_id.value,
            status=job.status,
            created_at=created_at_dt,
            message=f"Job {job.id.value} successfully queued and will be processed soon."
        )


def new_create_finetuning_job_presenter() -> CreateFinetuningJobPresenter:
    """
    CreateFinetuningJobPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return CreateFinetuningJobPresenterImpl()