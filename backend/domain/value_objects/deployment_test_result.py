# backend/domain/value_objects/deployment_test/deployment_test_result.py

from dataclasses import dataclass
from typing import List

# 他のV.O.をインポート
from .test_run_metrics import TestRunMetrics
from .inference_case_result import InferenceCaseResult 

@dataclass(frozen=True) 
class DeploymentTestResult:
    """テスト実行の結果全体（サマリーと全詳細）を保持するマスターV.O.（IDなし）"""
    overall_metrics: TestRunMetrics 
    case_results: List[InferenceCaseResult]