from typing import Dict, Union, Any

# ユースケース層の依存関係をインポート
from usecase.get_user_agents import (
    GetUserAgentsUseCase,
    GetUserAgentsInput,
    GetUserAgentsOutput,
)


class GetUserAgentsController:
    """
    特定ユーザーのエージェント一覧取得リクエストを処理し、ユースケースに委譲するコントローラ。
    """
    def __init__(self, uc: GetUserAgentsUseCase):
        """
        依存性注入によりユースケースインスタンスを受け取る。
        """
        self.uc = uc

    def execute(
        self, token: str
    ) -> Dict[str, Union[int, GetUserAgentsOutput, Dict[str, str]]]:
        """
        リクエストデータ（トークン）をユースケースのInputに変換し、実行結果をHTTP形式で返す。
        
        Args:
            token: ユーザーを認証するためのトークン文字列。
            
        Returns:
            Dict: HTTPステータスコードと結果データ（Output DTOまたはエラーメッセージ）を含む辞書。
        """
        # 1. Input DTOの生成
        input_data = GetUserAgentsInput(token=token)
        
        try:
            # 2. ユースケースの実行
            output: GetUserAgentsOutput
            err: Exception | None
            
            output, err = self.uc.execute(input_data)
            
            if err:
                # 3. エラー処理 (トークン無効、ユーザー不在、リポジトリエラーなど)
                # 一般的な認証エラーは 401 Unauthorized、その他のユースケースエラーは 400/404 も考慮される
                
                # ここでは認証失敗や一般的なユースケースエラーを401として扱う
                status_code = 401 if "token" in str(err).lower() or "auth" in str(err).lower() else 400
                
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 4. 成功レスポンス (200 OK)
            # GETリクエストなので 200 OK が適切
            return {"status": 200, "data": output}
            
        except Exception as e:
            # 5. 予期せぬサーバーエラー処理 (500 Internal Server Error)
            return {"status": 500, "data": {"error": f"An unexpected server error occurred: {e}"}}