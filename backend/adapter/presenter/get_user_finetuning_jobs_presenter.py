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
                created_at=job.created_at.isoformat(), # DBから来たdatetimeをISO文字列に変換
                finished_at=job.finished_at.isoformat() if job.finished_at else None, # 同上
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