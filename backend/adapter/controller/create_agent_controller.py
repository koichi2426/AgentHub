from typing import Dict, Union, Any
from usecase.create_agent import (
    CreateAgentUseCase,
    CreateAgentInput,
    CreateAgentOutput,
)


class CreateAgentController:
    def __init__(self, uc: CreateAgentUseCase):
        self.uc = uc

    def execute(
        self, input_data: CreateAgentInput
    ) -> Dict[str, Union[int, CreateAgentOutput, Dict[str, str]]]:
        try:
            output, err = self.uc.execute(input_data)
            if err:
                # トークン検証エラーやその他のユースケースエラー
                return {"status": 401, "data": {"error": str(err)}}
            
            # 成功
            return {"status": 201, "data": output}
        except Exception as e:
            # 予期せぬサーバーエラー
            return {"status": 500, "data": {"error": f"An unexpected error occurred: {e}"}}
