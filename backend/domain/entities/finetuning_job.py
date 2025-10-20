import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class FinetuningJob:
    id: ID
    agent_id: ID
    status: str  # e.g. 'completed' | 'running' | 'failed'
    created_at: Optional[str]
    finished_at: Optional[str]
    model_id: Optional[ID]


class FinetuningJobRepository(abc.ABC):
    @abc.abstractmethod
    def create_job(self, job: FinetuningJob) -> FinetuningJob:
        """
        ファインチューニングジョブを作成して返す
        """
        pass

    @abc.abstractmethod
    def find_by_id(self, job_id: "ID") -> Optional[FinetuningJob]:
        """
        ジョブIDからジョブを取得する
        """
        pass

    @abc.abstractmethod
    def list_by_agent(self, agent_id: "ID") -> list[FinetuningJob]:
        """
        指定エージェントに紐づくジョブ一覧を取得する
        """
        pass

    @abc.abstractmethod
    def update_status(self, job_id: "ID", status: str) -> None:
        """
        ジョブのステータスを更新する
        """
        pass

    @abc.abstractmethod
    def delete(self, job_id: "ID") -> None:
        """
        ジョブを削除する
        """
        pass


def NewFinetuningJob(
    id: int,
    agent_id: int,
    status: str,
    created_at: Optional[str],
    finished_at: Optional[str],
    model_id: Optional[int],
) -> FinetuningJob:
    return FinetuningJob(
        id=ID(id),
        agent_id=ID(agent_id),
        status=status,
        created_at=created_at,
        finished_at=finished_at,
        model_id=ID(model_id) if model_id is not None else None,
    )
