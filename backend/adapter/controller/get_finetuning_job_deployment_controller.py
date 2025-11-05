from typing import Dict, Union, Any
# ★ 参照するユースケースとDTOを 'GetFinetuningJobDeployment' のものに変更
from usecase.get_finetuning_job_deployment import (
    GetFinetuningJobDeploymentUseCase,
    GetFinetuningJobDeploymentInput,
    GetFinetuningJobDeploymentOutput,
)


class GetFinetuningJobDeploymentController:
    def __init__(self, uc: GetFinetuningJobDeploymentUseCase):
        self.uc = uc

    def execute(
        self, input_data: GetFinetuningJobDeploymentInput # ★ Input DTO を引数とする
    ) -> Dict[str, Union[int, GetFinetuningJobDeploymentOutput, Dict[str, str]]]:
        try:
            # ユースケースの実行
            output, err = self.uc.execute(input_data)
            
            if err:
                # 認証エラー(PermissionError)は 401、その他のロジックエラー(ValueError)は 400
                status_code = 401
                if isinstance(err, ValueError):
                    status_code = 400
                
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 成功 (GETリクエストの成功は 200 OK)
            return {"status": 200, "data": output}
            
        except Exception as e:
            # 予期せぬサーバーエラー
            return {"status": 500, "data": {"error": f"An unexpected error occurred: {e}"}}