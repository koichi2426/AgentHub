import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class Method:
    id: ID
    agent_id: ID
    name: str
    description: Optional[str]
    # 入出力の仕様を簡易的に格納するための自由形式フィールド
    interface_spec: Optional[dict]


class MethodRepository(abc.ABC):
    @abc.abstractmethod
    def list_by_agent(self, agent_id: str) -> list[Method]:
        """
        指定エージェントのメソッド一覧を取得する
        """
        pass

    @abc.abstractmethod
    def create(self, method: Method) -> Method:
        """
        メソッドを作成する
        """
        pass

    @abc.abstractmethod
    def find_by_id(self, method_id: str) -> Optional[Method]:
        """
        IDからメソッドを取得する
        """
        pass


def NewMethod(id: str, agent_id: str, name: str, description: Optional[str], interface_spec: Optional[dict]) -> Method:
    return Method(id=ID(id), agent_id=ID(agent_id), name=name, description=description, interface_spec=interface_spec)
