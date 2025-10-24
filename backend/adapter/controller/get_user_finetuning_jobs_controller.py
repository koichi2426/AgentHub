from typing import Dict, Union, Any, List

# ユースケース層の依存関係をインポート
from usecase.get_user_finetuning_jobs import (
    GetUserFinetuningJobsUseCase,
    GetUserFinetuningJobsInput,
    GetUserFinetuningJobsOutput,
)


class GetUserFinetuningJobsController:
    """
    特定ユーザーのファインチューニングジョブ一覧取得リクエストを処理し、ユースケースに委譲するコントローラ。
    """
    def __init__(self, uc: GetUserFinetuningJobsUseCase):
        """
        依存性注入によりユースケースインスタンスを受け取る。
        """
        self.uc = uc

    def execute(
        self, token: str
    ) -> Dict[str, Union[int, GetUserFinetuningJobsOutput, Dict[str, str]]]:
        """
        リクエストデータ（トークン）をユースケースのInputに変換し、実行結果をHTTP形式で返す。
        
        Args:
            token: ユーザーを認証するためのトークン文字列。
            
        Returns:
            Dict: HTTPステータスコードと結果データ（Output DTOまたはエラーメッセージ）を含む辞書。
        """
        # 1. Input DTOの生成
        input_data = GetUserFinetuningJobsInput(token=token)
        
        try:
            # 2. ユースケースの実行
            output: GetUserFinetuningJobsOutput
            err: Exception | None
            
            output, err = self.uc.execute(input_data)
            
            if err:
                # 3. エラー処理
                
                # 認証失敗や一般的な権限エラーを401として扱う
                status_code = 401
                
                # エラーメッセージに基づいて、より詳細なエラーコードを設定するロジック（例：トークン、authなど）は省略し、
                # 汎用的な認証エラーとして401を使用
                if "not found" in str(err).lower():
                    status_code = 404
                elif "permission" in str(err).lower():
                    status_code = 403
                
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 4. 成功レスポンス (200 OK)
            # GETリクエストなので 200 OK が適切
            return {"status": 200, "data": output}
            
        except Exception as e:
            # 5. 予期せぬサーバーエラー処理 (500 Internal Server Error)
            return {"status": 500, "data": {"error": f"An unexpected server error occurred: {e}"}}