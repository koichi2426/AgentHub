import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class Agent:
    id: ID
    user_id: ID  # ユーザーエンティティへの参照としてIDを追加
    owner: str  # username or user id
    name: str
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
    def list_by_user_id(self, user_id: "ID") -> list[Agent]:
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


def NewAgent(
    id: int, user_id: int, owner: str, name: str, description: Optional[str]
) -> Agent:
    """
    Agentエンティティを生成するファクトリ関数
    """
    return Agent(
        id=ID(id),
        user_id=ID(user_id),
        owner=owner,
        name=name,
        description=description,
    )

