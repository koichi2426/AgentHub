from typing import Dict, Union

from usecase.auth_signup import (
    CreateUserUseCase,
    CreateUserInput,
    CreateUserOutput,
)


class CreateUserController:
    def __init__(self, uc: CreateUserUseCase):
        self.uc = uc

    def execute(
        self, input_data: CreateUserInput
    ) -> Dict[str, Union[int, CreateUserOutput, Dict[str, str]]]:
        try:
            output, err = self.uc.execute(input_data)
            if err:
                return {"status": 400, "data": {"error": str(err)}}
            return {"status": 201, "data": output}
        except Exception:
            return {"status": 500, "data": {"error": "An unexpected error occurred"}}
