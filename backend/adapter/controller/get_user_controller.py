from typing import Dict, Union, Any
from usecase.get_user import (
    GetUserUseCase,
    GetUserInput,
)


class GetUserController:
    def __init__(self, uc: GetUserUseCase):
        self.uc = uc

    def execute(
        self, input_data: GetUserInput
    ) -> Dict[str, Union[int, Dict[str, Any], Dict[str, str]]]:
        try:
            # ユースケースを実行して、結果(output)とエラー(err)を取得
            output, err = self.uc.execute(input_data)

            # エラーがあれば、ステータス401とエラーメッセージを返す
            if err:
                return {"status": 401, "data": {"error": str(err)}}

            # 成功すれば、ステータス200とユーザーデータを返す
            return {"status": 200, "data": output}
        except Exception:
            # 予期せぬサーバーエラーが発生した場合
            return {"status": 500, "data": {"error": "An unexpected error occurred"}}
