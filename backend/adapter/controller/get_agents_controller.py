from typing import Dict, Union, Any

# ユースケース層の依存関係をインポート
# GetUserAgents から GetAgents に修正
from usecase.get_agents import (
    GetAgentsUseCase,
    GetAgentsInput,
    GetAgentsOutput,
)


# クラス名を GetAgentsController に修正
class GetAgentsController:
    """
    全エージェント一覧取得リクエストを処理し、ユースケースに委譲するコントローラ。
    """
    # ユースケースの型を GetAgentsUseCase に修正
    def __init__(self, uc: GetAgentsUseCase):
        """
        依存性注入によりユースケースインスタンスを受け取る。
        """
        self.uc = uc

    # token引数を削除し、input_data (GetAgentsInput) を直接受け取るように修正
    def execute(
        self, input_data: GetAgentsInput
    ) -> Dict[str, Union[int, GetAgentsOutput, Dict[str, str]]]:
        """
        リクエストデータ（Input）をユースケースに渡し、実行結果をHTTP形式で返す。
        """
        # 実行結果として、Output DTOと例外を受け取る
        output: GetAgentsOutput
        err: Exception | None

        try:
            # 2. ユースケースの実行
            output, err = self.uc.execute(input_data)
            
            if err:
                # 3. エラー処理 (DBエラーなど)
                
                status_code = 400
                
                # エラーメッセージに基づいてステータスコードを判断
                if "not found" in str(err).lower():
                    status_code = 404
                # 全件取得に認証エラーは発生しないため、認証ロジックは削除
                
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 4. 成功レスポンス (200 OK)
            return {"status": 200, "data": output}
            
        except Exception as e:
            # 5. 予期せぬサーバーエラー処理 (500 Internal Server Error)
            return {"status": 500, "data": {"error": f"An unexpected server error occurred: {e}"}}