import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional, List

# ユースケース層の依存関係
# GetUserAgents ではなく GetAgents をインポート
from usecase.get_agents import GetAgentsPresenter, GetAgentsOutput, AgentListItem 
# ドメイン層の依存関係
from domain.entities.agent import Agent


class GetAgentsPresenterImpl(GetAgentsPresenter):
    """
    全エージェント取得ユースケース (GetAgentsUseCase) のPresenter具体的な実装。
    AgentドメインオブジェクトのリストをGetAgentsOutput DTOに変換する。
    """
    def output(self, agents: List[Agent]) -> GetAgentsOutput:
        """
        Agentドメインオブジェクトのリストを GetAgentsOutput DTO に変換して返す。
        """
        # ドメインオブジェクトのリストを Output DTO のリスト (AgentListItem) に変換
        agent_list_items = [
            AgentListItem(
                # IDの値オブジェクトから値 (.value) を取り出すことを想定
                id=agent.id.value,
                user_id=agent.user_id.value,
                owner=agent.owner,
                name=agent.name,
                description=agent.description,
            )
            for agent in agents
        ]

        # 最終的な Output DTO に格納して返す
        return GetAgentsOutput(
            agents=agent_list_items
        )


def new_get_agents_presenter() -> GetAgentsPresenter:
    """
    GetAgentsPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return GetAgentsPresenterImpl()