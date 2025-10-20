import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class Agent:
    id: ID
    name: str
    owner: str  # username or user id
    description: Optional[str]


class AgentRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, agent: Agent) -> Agent:
        """
        エージェントを作成して返す
        """
        pass

    @abc.abstractmethod
    def find_by_id(self, agent_id: "ID") -> Optional[Agent]:
        """
        IDからエージェントを検索する
        """
        pass

    @abc.abstractmethod
    def find_by_owner_and_name(self, owner: str, name: str) -> Optional[Agent]:
        """
        owner と agent name から特定のエージェントを取得する
        """
        pass

    @abc.abstractmethod
    def list_by_owner(self, owner: str) -> list[Agent]:
        """
        指定ユーザーのエージェント一覧を取得する
        """
        pass

    @abc.abstractmethod
    def find_all(self) -> list[Agent]:
        """
        すべてのエージェントを取得する
        """
        pass

    @abc.abstractmethod
    def update(self, agent: Agent) -> None:
        """
        エージェント情報を更新する
        """
        pass

    @abc.abstractmethod
    def delete(self, agent_id: "ID") -> None:
        """
        IDでエージェントを削除する
        """
        pass


def NewAgent(id: int, name: str, owner: str, description: Optional[str]) -> Agent:
    return Agent(id=ID(id), name=name, owner=owner, description=description)
