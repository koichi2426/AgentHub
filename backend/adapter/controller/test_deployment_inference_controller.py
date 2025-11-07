# backend/adapter/controller/test_deployment_inference_controller.py

from typing import Dict, Union, Any
from usecase.test_deployment_inference import (
    TestDeploymentInferenceUseCase,
    TestDeploymentInferenceInput,
    TestDeploymentInferenceOutput,
)


class TestDeploymentInferenceController:
    """
    デプロイメントの推論テストリクエストを処理し、ユースケースに委譲するコントローラ。
    """
    def __init__(self, uc: TestDeploymentInferenceUseCase):
        """
        依存性注入によりユースケースインスタンスを受け取る。
        """
        self.uc = uc

    def execute(
        self, input_data: TestDeploymentInferenceInput
    ) -> Dict[str, Union[int, TestDeploymentInferenceOutput, Dict[str, str]]]:
        """
        Input DTOを受け取り、ユースケースを実行する。
        """
        
        try:
            # 1. ユースケースの実行
            output: TestDeploymentInferenceOutput
            err: Exception | None
            
            output, err = self.uc.execute(input_data)
            
            if err:
                # 2. エラー処理
                
                status_code = 500 
                
                # 権限不足/認証エラー (403)
                if "permission" in str(err).lower() or "token" in str(err).lower():
                    status_code = 403
                # リソースNotFound (404)
                elif "not found" in str(err).lower() or "non-existent" in str(err).lower():
                    status_code = 404
                # ロジックエラー (400)
                elif isinstance(err, (ValueError, FileExistsError)):
                    status_code = 400
                
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 3. 成功レスポンス (200 OK)
            return {"status": 200, "data": output}
            
        except Exception as e:
            # 4. 予期せぬサーバーエラー処理 (500 Internal Server Error)
            return {"status": 500, "data": {"error": f"An unexpected error occurred: {e}"}}