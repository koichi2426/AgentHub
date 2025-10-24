from usecase.create_agent import CreateAgentPresenter, CreateAgentOutput
from domain.entities.agent import Agent


class CreateAgentPresenterImpl(CreateAgentPresenter):
    def output(self, agent: Agent) -> CreateAgentOutput:
        """
        Agentドメインオブジェクトを CreateAgentOutput DTO に変換して返す。
        """
        return CreateAgentOutput(
            id=agent.id.value,
            user_id=agent.user_id.value,
            owner=agent.owner,
            name=agent.name,
            description=agent.description,
        )


def new_create_agent_presenter() -> CreateAgentPresenter:
    """
    CreateAgentPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return CreateAgentPresenterImpl()

