from typing import List

# ユースケース層の依存関係
from usecase.get_user_agents import GetUserAgentsPresenter, GetUserAgentsOutput, AgentListItem
# ドメイン層の依存関係
from domain.entities.agent import Agent


class GetUserAgentsPresenterImpl(GetUserAgentsPresenter):
    def output(self, agents: List[Agent]) -> GetUserAgentsOutput:
        """
        Agentドメインオブジェクトのリストを GetUserAgentsOutput DTO に変換して返す。
        """
        # ドメインオブジェクトのリストを Output DTO のリスト (AgentListItem) に変換
        agent_list_items = [
            AgentListItem(
                id=agent.id.value,
                user_id=agent.user_id.value,
                owner=agent.owner,
                name=agent.name,
                description=agent.description,
            )
            for agent in agents
        ]

        # 最終的な Output DTO に格納して返す
        return GetUserAgentsOutput(
            agents=agent_list_items
        )


def new_get_user_agents_presenter() -> GetUserAgentsPresenter:
    """
    GetUserAgentsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetUserAgentsPresenterImpl()