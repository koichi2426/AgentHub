# backend/adapter/controller/create_finetuning_job_controller.py

from typing import Dict, Union, Any
from usecase.create_finetuning_job import (
    CreateFinetuningJobUseCase,
    CreateFinetuningJobInput,
    CreateFinetuningJobOutput,
)
from fastapi import UploadFile

# Adapter (実装)と抽象クラス (インターフェース) をインポート
from infrastructure.domain.value_objects.file_data_impl import FastAPIUploadedFileAdapter
from domain.value_objects.file_data import UploadedFileStream


class CreateFinetuningJobController:
    def __init__(self, uc: CreateFinetuningJobUseCase):
        self.uc = uc

    def execute(
        self, token: str, agent_id: int, uploaded_file: UploadFile
    ) -> Dict[str, Union[int, CreateFinetuningJobOutput, Dict[str, str]]]:
        """
        ファイルアップロードとジョブ投入リクエストを処理し、ユースケースに委譲する。
        """
        try:
            # 1. インフラの型 (UploadFile) をドメインの抽象型 (UploadedFileStream) に適合させる
            domain_file: UploadedFileStream = FastAPIUploadedFileAdapter(uploaded_file)
            
            # 2. Input DTO の生成
            input_data = CreateFinetuningJobInput(
                token=token,
                agent_id=agent_id,
                training_file=domain_file
            )
            
            # 3. ユースケースの実行
            output, err = self.uc.execute(input_data)
            
            if err:
                # 認証エラー(PermissionError)は 401、その他のロジックエラー(ValueError)は 400
                status_code = 401 if isinstance(err, PermissionError) else 400
                return {"status": status_code, "data": {"error": str(err)}}
            
            # 4. 成功レスポンス (ジョブを受け付けたため、201 Created を使用)
            # NOTE: キューイングの場合、厳密には 202 Accepted が適切だが、既存のコード形式に合わせ 201 を使用。
            return {"status": 201, "data": output}
            
        except Exception as e:
            # 5. 予期せぬサーバーエラー (ファイル操作エラーなど)
            return {"status": 500, "data": {"error": f"An unexpected error occurred: {e}"}}