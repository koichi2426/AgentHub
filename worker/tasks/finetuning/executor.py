# AGENTHUB/worker/tasks/finetuning/executor.py

import time
from datetime import datetime as PythonDateTime
from typing import Optional

# NOTE: ここではDB接続を行いません。成功ログとダミーのModel IDを返すだけです。

def execute_finetuning_pipeline(job_id: int, file_path: str) -> None:
    """
    ファインチューニングジョブの実行パイプライン（モック）。
    このモックは、ジョブがすぐに成功したと仮定し、DBリポジトリの
    update_status メソッドが外部で呼ばれることを示唆する。
    """
    
    print(f"INFO: Job {job_id}: Pipeline starting (MOCK). File path: {file_path}")
    
    # 処理に時間がかかることをシミュレート
    time.sleep(2) 
    
    # ジョブが完了したことを示すダミー情報を生成
    model_id = f"mock-model-{job_id}-SUCCESS"
    finished_time = PythonDateTime.utcnow().isoformat()
    
    print(f"SUCCESS: Job {job_id} finished (MOCK). Model ID: {model_id}")
    
    # NOTE: 実際にはここで job_repo.update_status(ID(job_id), 'completed', ...) を呼び出します。
    # この最低限の実装では、DB更新のロジックは省略し、正常終了することのみを保証します。
    
    pass