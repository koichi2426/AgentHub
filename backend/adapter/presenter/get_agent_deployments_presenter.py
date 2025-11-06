from typing import List, Optional

# ユースケース層の依存関係をインポート
from usecase.get_agent_deployments import (
    GetAgentDeploymentsPresenter,
    GetAgentDeploymentsOutput,
    DeploymentListItem
)
# ドメイン層の依存関係をインポート
from domain.entities.deployment import Deployment


class GetAgentDeploymentsPresenterImpl(GetAgentDeploymentsPresenter):
    def output(self, deployments: List[Deployment]) -> GetAgentDeploymentsOutput:
        """
        Deploymentドメインオブジェクトのリストを GetAgentDeploymentsOutput DTO に変換して返す。
        """
        # ドメインオブジェクトのリストを Output DTO のリスト (DeploymentListItem) に変換
        deployment_list_items = [
            DeploymentListItem(
                id=d.id.value,
                job_id=d.job_id.value,
                status=d.status,
                endpoint=d.endpoint,
            )
            for d in deployments
        ]

        # 最終的な Output DTO に格納して返す
        return GetAgentDeploymentsOutput(
            deployments=deployment_list_items
        )


def new_get_agent_deployments_presenter() -> GetAgentDeploymentsPresenter:
    """
    GetAgentDeploymentsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetAgentDeploymentsPresenterImpl()