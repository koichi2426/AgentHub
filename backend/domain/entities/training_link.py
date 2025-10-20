import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class TrainingLink:
    job_id: ID
    data_url: Optional[str]
    file_name: Optional[str]
    record_count: Optional[int]
    file_size: Optional[str]


class TrainingDataRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, link: TrainingLink) -> TrainingLink:
        """
        学習データリンクを作成して返す
        """
        pass

    @abc.abstractmethod
    def find_by_job(self, job_id: "ID") -> Optional[TrainingLink]:
        """
        ジョブIDから学習データリンクを取得する
        """
        pass

    @abc.abstractmethod
    def update(self, link: TrainingLink) -> None:
        """
        学習データリンクのメタ情報を更新する
        """
        pass


def NewTrainingLink(
    job_id: str,
    data_url: Optional[str],
    file_name: Optional[str],
    record_count: Optional[int],
    file_size: Optional[str],
) -> TrainingLink:
    return TrainingLink(job_id=ID(job_id), data_url=data_url, file_name=file_name, record_count=record_count, file_size=file_size)
