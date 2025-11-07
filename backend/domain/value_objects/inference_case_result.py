# backend/domain/value_objects/deployment_test/inference_case_result.py

from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True) 
class InferenceCaseResult:
    """個々のテストケースの結果と生データを保持するV.O.（IDなし）"""
    input_data: str
    expected_output: str
    predicted_output: str
    is_correct: bool
    
    # 外部エンジンからの生レスポンスデータ
    raw_engine_response: Dict[str, Any]
    
    # 外部電力計測APIからの生データ
    raw_power_response: Dict[str, Any]