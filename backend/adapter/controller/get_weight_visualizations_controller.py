import abc
from typing import Dict, Union, Any, List

# ユースケース層の依存関係をインポート
from usecase.get_weight_visualizations import (
    GetFinetuningJobVisualizationUseCase,
    GetFinetuningJobVisualizationInput,
    GetFinetuningJobVisualizationOutput,
)


class GetWeightVisualizationsController:
    """
    特定のジョブの重み可視化データ取得リクエストを処理し、ユースケースに委譲するコントローラ。
    """
    def __init__(self, uc: GetFinetuningJobVisualizationUseCase):
        """
        依存性注入によりユースケースインスタンスを受け取る。
        """
        self.uc = uc

    def execute(
        self, token: str, job_id: int
    ) -> Dict[str, Union[int, GetFinetuningJobVisualizationOutput, Dict[str, str]]]:
        """
        リクエストデータ（トークンとジョブID）をユースケースのInputに変換し、実行結果をHTTP形式で返す。
        
        Args:
            token: ユーザーを認証するためのトークン文字列。
            job_id: 取得したいジョブのID。
            
        Returns:
            Dict: HTTPステータスコードと結果データ（Output DTOまたはエラーメッセージ）を含む辞書。
        """
        # 1. Input DTOの生成
        input_data = GetFinetuningJobVisualizationInput(token=token, job_id=job_id)
        
        try:
            # 2. ユースケースの実行
            output: GetFinetuningJobVisualizationOutput
            err: Exception | None
            
            output, err = self.uc.execute(input_data)
            
            if err:
                # 3. エラー処理
                status_code = 500 # デフォルトはサーバーエラー

                # エラーメッセージを判定
                err_str = str(err).lower()
                
                if "not found" in err_str:
                    status_code = 404
                elif "permission" in err_str or "auth" in err_str:
                    status_code = 403 # 権限または認証エラー
                elif "token" in err_str:
                    status_code = 401 # トークンエラー
                
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 4. 成功レスポンス (200 OK)
            # GETリクエストなので 200 OK が適切
            return {"status": 200, "data": output}
            
        except Exception as e:
            # 5. 予期せぬサーバーエラー処理 (500 Internal Server Error)
            return {"status": 500, "data": {"error": f"An unexpected server error occurred: {e}"}}
