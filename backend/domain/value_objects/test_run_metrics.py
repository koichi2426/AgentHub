# backend/domain/value_objects/deployment_test/test_run_metrics.py

from dataclasses import dataclass

@dataclass(frozen=True) 
class TestRunMetrics:
    """全体の評価メトリクス（平均時間、精度、コスト）を保持するV.O."""
    accuracy: float
    latency_ms: float       # ナノ秒から計算した平均推論時間 (ミリ秒)
    cost_estimate_mwh: float  # 推論あたりの平均エネルギーコスト (mWh)
    total_test_cases: int
    correct_predictions: int