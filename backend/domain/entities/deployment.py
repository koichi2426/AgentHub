import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class Deployment:
    id: ID
    job_id: ID
    status: str
    endpoint: Optional[str]
    deployed_at: Optional[str]


class DeploymentRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, deployment: Deployment) -> Deployment:
        """
        デプロイメントを作成して返す
        """
        pass

    @abc.abstractmethod
    def find_by_id(self, deployment_id: "ID") -> Optional[Deployment]:
        """
        IDからデプロイメントを取得する
        """
        pass

    @abc.abstractmethod
    def list_by_agent(self, agent_id: "ID") -> list[Deployment]:
        """
        指定エージェントに関連するデプロイメント一覧を取得する
        """
        pass

    @abc.abstractmethod
    def find_by_job_id(self, job_id: "ID") -> list[Deployment]:
        """
        job_id に紐づくデプロイメントを検索する
        """
        pass

    @abc.abstractmethod
    def delete(self, deployment_id: "ID") -> None:
        """
        デプロイメントを削除する
        """
        pass


def NewDeployment(
    id: int,
    job_id: int,
    status: str,
    endpoint: Optional[str],
    deployed_at: Optional[str],
) -> Deployment:
    return Deployment(id=ID(id), job_id=ID(job_id), status=status, endpoint=endpoint, deployed_at=deployed_at)