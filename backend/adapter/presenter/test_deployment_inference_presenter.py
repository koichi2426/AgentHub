# backend/adapter/presenter/test_deployment_inference_presenter.py

from typing import List, Dict, Any

# ユースケース層の依存関係
from usecase.test_deployment_inference import (
    TestDeploymentInferencePresenter,
    TestDeploymentInferenceOutput,
    TestMetricsOutput,
)
# ドメイン層の Value Objects をインポート
from domain.value_objects.deployment_test_result import DeploymentTestResult
from domain.value_objects.test_run_metrics import TestRunMetrics 
from domain.value_objects.inference_case_result import InferenceCaseResult


class TestDeploymentInferencePresenterImpl(TestDeploymentInferencePresenter):
    
    def output(self, result: DeploymentTestResult) -> TestDeploymentInferenceOutput:
        """
        DeploymentTestResult V.O. を Output DTO に変換して返す。
        V.O.からデータを抽出し、ネストされた Dict 構造を作成する。
        """

        overall_metrics_dict: Dict[str, Any] = {
            "accuracy": result.overall_metrics.accuracy,
            "latency_ms": result.overall_metrics.latency_ms,
            "cost_estimate_mwh": result.overall_metrics.cost_estimate_mwh,
            "total_test_cases": result.overall_metrics.total_test_cases,
            "correct_predictions": result.overall_metrics.correct_predictions,
        }
        
        case_results_list: List[Dict[str, Any]] = [
            {
                "id": idx + 1,
                "input_data": case.input_data,
                "expected_output": case.expected_output,
                "predicted_output": case.predicted_output,
                "is_correct": case.is_correct,
                "raw_engine_response": case.raw_engine_response,
                "raw_power_response": case.raw_power_response,
            }
            for idx, case in enumerate(result.case_results)
        ]
        
        test_metrics_output = TestMetricsOutput(
            overall_metrics=overall_metrics_dict,
            case_results=case_results_list
        )
        
        return TestDeploymentInferenceOutput(
            test_result=test_metrics_output,
            message="Deployment test run successfully."
        )


def new_test_deployment_inference_presenter() -> TestDeploymentInferencePresenter:
    """
    TestDeploymentInferencePresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return TestDeploymentInferencePresenterImpl()