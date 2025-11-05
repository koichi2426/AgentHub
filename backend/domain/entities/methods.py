# backend/domain/entities/methods.py
import abc
from dataclasses import dataclass, field
from typing import List, Optional

from ..value_objects.id import ID
from ..value_objects.method import Method


@dataclass
class DeploymentMethods:
    """
    特定のデプロイメントに紐づくメソッド（機能）の集合を表すエンティティ。
    """
    id: ID
    deployment_id: ID
    methods: List[Method] = field(default_factory=list)

    def get_method_names(self) -> List[str]:
        """
        メソッド名のリスト（文字列）を返すヘルパー
        """
        return [method.name for method in self.methods]


class DeploymentMethodsRepository(abc.ABC):
    """
    DeploymentMethodsエンティティの永続化を管理するリポジトリ（I/F）
    """
    @abc.abstractmethod
    def find_by_deployment_id(self, deployment_id: ID) -> Optional[DeploymentMethods]:
        """
        デプロイメントIDからメソッドの集合を取得する
        """
        pass
    
    @abc.abstractmethod
    def find_by_id(self, id: ID) -> Optional[DeploymentMethods]:
        """
        このエンティティ自体のIDから取得する
        """
        pass

    @abc.abstractmethod
    def save(self, deployment_methods: DeploymentMethods) -> DeploymentMethods:
        """
        メソッドの集合を保存（作成または更新）する
        """
        pass

    @abc.abstractmethod
    def delete_by_deployment_id(self, deployment_id: ID) -> None:
        """
        デプロイメントIDに紐づくメソッドの集合を削除する
        """
        pass


def NewDeploymentMethods(
    id: int,
    deployment_id: int,
    method_names: List[str]
) -> DeploymentMethods:
    """
    プリミティブな値から DeploymentMethods エンティティを生成するファクトリ関数。
    
    フロントのJSON (id: "m_entry_001") とは異なり、
    バックエンドのドメインルール (id: int) に従って生成します。
    """
    
    # 文字列のリストを Method 値オブジェクトのリストに変換
    method_vos = [Method(name=name) for name in method_names if name]
    
    return DeploymentMethods(
        id=ID(id),
        deployment_id=ID(deployment_id),
        methods=method_vos
    )