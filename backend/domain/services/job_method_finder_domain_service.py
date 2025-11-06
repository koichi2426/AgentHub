import abc
from typing import Protocol, List

# 必要な「道具」となる値オブジェクトをインポート
from ..value_objects.id import ID
from ..value_objects.method import Method


class JobMethodFinderDomainService(Protocol):
    """
    ジョブIDに基づき、それに関連する（デプロイメントの）
    メソッド（Method）リストを取得するドメインサービスの「設計図（I/F）」。

    責務：
    「job_id」から「Methodのリスト」をどうやって見つけるか、
    という（もしかしたら複数のリポジトリをまたぐかもしれない）
    ビジネスルールをカプセル化（隠蔽）すること。

    ファイル名と命名規則を合わせるため、
    "JobMethodFinder" + "DomainService" というクラス名にしています。
    """

    @abc.abstractmethod
    def find_methods_by_job_id(self, job_id: ID) -> List[Method]:
        """
        ジョブIDに紐づくメソッドのリストを返す。

        ロジック（実装）はインフラ層に委譲される。
        （例：JobRepository -> DeploymentRepository -> DeploymentMethodsRepository）

        Args:
            job_id: 検索対象のジョブID（値オブジェクト）。

        Returns:
            List[Method]: Method値オブジェクトのリスト。
                          見つからない場合は空のリストを返す。
        """
        ...