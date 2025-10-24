from typing import Dict, Union, Any
from usecase.create_finetuning_job import (
    CreateFinetuningJobUseCase,
    CreateFinetuningJobInput,
    CreateFinetuningJobOutput,
)


class CreateFinetuningJobController:
    def __init__(self, uc: CreateFinetuningJobUseCase):
        self.uc = uc

    def execute(
        self, input_data: CreateFinetuningJobInput # ★ 忠実に Input DTO を引数とする ★
    ) -> Dict[str, Union[int, CreateFinetuningJobOutput, Dict[str, str]]]:
        try:
            # ユースケースの実行
            output, err = self.uc.execute(input_data)
            
            if err:
                # 認証エラー(PermissionError)は 401、その他のロジックエラー(ValueError)は 400
                status_code = 401
                if isinstance(err, ValueError):
                    status_code = 400
                
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 成功 (ジョブ作成/キューイングは 201 Created を使用)
            return {"status": 201, "data": output}
            
        except Exception as e:
            # 予期せぬサーバーエラー
            return {"status": 500, "data": {"error": f"An unexpected error occurred: {e}"}}