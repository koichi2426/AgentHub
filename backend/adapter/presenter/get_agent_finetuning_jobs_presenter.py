from typing import List, Optional

# ユースケース層の依存関係
from usecase.get_agent_finetuning_jobs import (
    GetAgentFinetuningJobsPresenter, # ★ クラス名を修正
    GetAgentFinetuningJobsOutput,    # ★ クラス名を修正
    FinetuningJobListItem
)
# ドメイン層の依存関係
from domain.entities.finetuning_job import FinetuningJob


class GetAgentFinetuningJobsPresenterImpl(GetAgentFinetuningJobsPresenter): # ★ クラス名を修正
    def output(self, jobs: List[FinetuningJob]) -> GetAgentFinetuningJobsOutput: # ★ クラス名を修正
        """
        FinetuningJobドメインオブジェクトのリストを GetAgentFinetuningJobsOutput DTO に変換して返す。
        """
        # ドメインオブジェクトのリストを Output DTO のリスト (FinetuningJobListItem) に変換
        job_list_items = [
            FinetuningJobListItem(
                id=job.id.value,
                agent_id=job.agent_id.value,
                status=job.status,
                training_file_path=job.training_file_path,
                created_at=job.created_at.isoformat(),
                finished_at=job.finished_at.isoformat() if job.finished_at else None,
                error_message=job.error_message,
            )
            for job in jobs
        ]

        # 最終的な Output DTO に格納して返す
        return GetAgentFinetuningJobsOutput( # ★ クラス名を修正
            jobs=job_list_items
        )


def new_get_agent_finetuning_jobs_presenter() -> GetAgentFinetuningJobsPresenter: # ★ 関数名を修正
    """
    GetAgentFinetuningJobsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetAgentFinetuningJobsPresenterImpl() # ★ クラス名を修正