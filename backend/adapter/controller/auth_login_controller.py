from typing import Dict, Union
from usecase.auth_login import (
    LoginUserUseCase,
    LoginUserInput,
    LoginUserOutput,
)


class LoginUserController:
    def __init__(self, uc: LoginUserUseCase):
        self.uc = uc

    def execute(
        self, input_data: LoginUserInput
    ) -> Dict[str, Union[int, LoginUserOutput, Dict[str, str]]]:
        try:
            output, err = self.uc.execute(input_data)
            if err:
                # ユースケースからのエラー（例：認証失敗）
                return {"status": 401, "data": {"error": str(err)}}
            
            # 成功
            return {"status": 200, "data": output}
        except Exception:
            # 予期せぬサーバーエラー
            return {"status": 500, "data": {"error": "An unexpected error occurred"}}
