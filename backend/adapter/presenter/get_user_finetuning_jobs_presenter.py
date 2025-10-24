from typing import List, Optional

# ユースケース層の依存関係
from usecase.get_user_finetuning_jobs import (
    GetUserFinetuningJobsPresenter, 
    GetUserFinetuningJobsOutput, 
    FinetuningJobListItem
)
# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJob


class GetUserFinetuningJobsPresenterImpl(GetUserFinetuningJobsPresenter):
    def output(self, jobs: List[FinetuningJob]) -> GetUserFinetuningJobsOutput:
        """
        FinetuningJobドメインオブジェクトのリストを GetUserFinetuningJobsOutput DTO に変換して返す。
        """
        # ドメインオブジェクトのリストを Output DTO のリスト (FinetuningJobListItem) に変換
        job_list_items = [
            FinetuningJobListItem(
                id=job.id.value,
                agent_id=job.agent_id.value,
                status=job.status,
                training_file_path=job.training_file_path,
                # model_id は Optional[ID] なので、値が存在すればその .value を、なければ None を使用
                model_id=job.model_id.value if job.model_id else None,
                # created_at と finished_at は、エンティティ内で既に str (ISO 8601) または datetime
                # (ユースケースで str に変換済み)として扱われている前提でそのまま渡す
                created_at=job.created_at,
                finished_at=job.finished_at,
                error_message=job.error_message,
            )
            for job in jobs
        ]

        # 最終的な Output DTO に格納して返す
        return GetUserFinetuningJobsOutput(
            jobs=job_list_items
        )


def new_get_user_finetuning_jobs_presenter() -> GetUserFinetuningJobsPresenter:
    """
    GetUserFinetuningJobsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetUserFinetuningJobsPresenterImpl()