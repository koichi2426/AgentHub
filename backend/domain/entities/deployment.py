import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class Deployment:
    id: ID
    model_id: ID
    status: str  # e.g. 'active' | 'inactive'
    endpoint: Optional[str]
    created_at: Optional[str]


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
    def find_by_model_id(self, model_id: "ID") -> list[Deployment]:
        """
        model_id に紐づくデプロイメントを検索する
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
    model_id: int,
    status: str,
    endpoint: Optional[str],
    created_at: Optional[str],
) -> Deployment:
    return Deployment(id=ID(id), model_id=ID(model_id), status=status, endpoint=endpoint, created_at=created_at)
