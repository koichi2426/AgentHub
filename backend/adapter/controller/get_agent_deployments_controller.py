from typing import Dict, Union, Any, List

# ユースケース層の依存関係をインポート
# ★★★ 修正: 参照するユースケースを GetAgentDeployments に変更 ★★★
from usecase.get_agent_deployments import (
    GetAgentDeploymentsUseCase, 
    GetAgentDeploymentsInput,   
    GetAgentDeploymentsOutput,  
)


class GetAgentDeploymentsController: 
    """
    特定Agentのデプロイメント一覧取得リクエストを処理し、ユースケースに委譲するコントローラ。
    """
    def __init__(self, uc: GetAgentDeploymentsUseCase): # ★ ユースケースクラス名を修正
        """
        依存性注入によりユースケースインスタンスを受け取る。
        """
        self.uc = uc

    def execute(
        self, token: str, agent_id: int 
    ) -> Dict[str, Union[int, GetAgentDeploymentsOutput, Dict[str, str]]]: # ★ Outputクラス名を修正
        """
        リクエストデータ（トークンとagent_id）をユースケースのInputに変換し、実行結果をHTTP形式で返す。
        
        Args:
            token: ユーザーを認証するためのトークン文字列。
            agent_id: 対象のAgent ID。
            
        Returns:
            Dict: HTTPステータスコードと結果データ（Output DTOまたはエラーメッセージ）を含む辞書。
        """
        # 1. Input DTOの生成
        # ★ 修正: Input DTOクラス名を修正 ★
        input_data = GetAgentDeploymentsInput(token=token, agent_id=agent_id)
        
        try:
            # 2. ユースケースの実行
            output: GetAgentDeploymentsOutput # ★ Outputクラス名を修正
            err: Exception | None
            
            output, err = self.uc.execute(input_data)
            
            if err:
                # 3. エラー処理
                
                # 認証失敗や一般的な権限エラーを401として扱う
                status_code = 401
                
                # エラーメッセージに基づいて、より詳細なエラーコードを設定するロジックは省略
                if "not found" in str(err).lower():
                    status_code = 404
                elif "permission" in str(err).lower():
                    status_code = 403
                
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 4. 成功レスポンス (200 OK)
            return {"status": 200, "data": output}
            
        except Exception as e:
            # 5. 予期せぬサーバーエラー処理 (500 Internal Server Error)
            return {"status": 500, "data": {"error": f"An unexpected server error occurred: {e}"}}