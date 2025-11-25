# backend/infrastructure/domain/services/deployment_test_domain_service_impl.py

import asyncio
import json
import httpx
import os
from typing import List, Dict, Any, Optional

from domain.value_objects.file_data import UploadedFileStream
from domain.services.deployment_test_domain_service import DeploymentTestDomainService
from domain.value_objects.deployment_test_result import DeploymentTestResult
from domain.value_objects.inference_case_result import InferenceCaseResult
from domain.value_objects.test_run_metrics import TestRunMetrics

POWER_API_URL = os.environ.get("POWER_MONITOR_API_URL", "http://localhost:8080/power")


class DeploymentTestDomainServiceImpl(DeploymentTestDomainService):
    """デプロイメントテスト実行の具体的な実装。"""
    MAX_CONCURRENCY = 1  # 並列実行数を制限
    THRESHOLD = 0.6  # 類似度閾値

    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    # ---------------------------
    # ヘルパー: 推論出力抽出
    # ---------------------------
    def _extract_predicted_output(self, engine_response: Dict[str, Any]) -> tuple[str, float]:
        """推論結果からメソッド名と類似度を抽出する。
        
        Returns:
            tuple[str, float]: (メソッド名, 類似度スコア)
        """
        results = engine_response.get("results")
        if results and isinstance(results, list) and len(results) > 0:
            top_result = results[0]
            method = str(top_result.get("method", "")).strip()
            similarity = float(top_result.get("similarity", 0.0))
            return method, similarity
        return "", 0.0

    # ---------------------------
    # 電力メトリクス取得
    # ---------------------------
    async def _get_power_metrics(self) -> Dict[str, Any]:
        try:
            response = await self._client.get(POWER_API_URL, timeout=5)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return {"status": "error", "power_watts": "0.0", "timestamp_ns": "0"}

    # ---------------------------
    # 推論実行
    # ---------------------------
    async def _run_single_inference(self, endpoint_url: str, input_text: str) -> Dict[str, Any]:
        try:
            payload = {"prompt": input_text}
            response = await self._client.post(endpoint_url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            msg = f"Client error '{e.response.status_code} {e.response.reason_phrase}' for url '{endpoint_url}'"
            return {"status": "error", "error_detail": msg, "results": []}
        except Exception as e:
            return {"status": "error", "error_detail": f"Connection Error: {str(e)}", "results": []}

    # ---------------------------
    # 単一テストケース処理
    # ---------------------------
    async def _process_single_test_case(self, endpoint_url: str, input_line: str, expected_output: str) -> Optional[InferenceCaseResult]:
        try:
            power_base_response = await self._get_power_metrics()
            inference_future = self._run_single_inference(endpoint_url, input_line)

            engine_response, power_active_response = await asyncio.gather(
                inference_future, self._get_power_metrics()
            )

            predicted_output, similarity_score = self._extract_predicted_output(engine_response)
            
            # 正解判定ロジック
            if expected_output.lower() == "none":
                # 何もしないことが正解の場合: スコアが低ければ正解
                is_correct = similarity_score < self.THRESHOLD
            else:
                # 特定のメソッドが正解の場合: 一致 & スコアが閾値以上
                is_correct = (predicted_output.lower() == expected_output.lower() and 
                             similarity_score >= self.THRESHOLD)

            return InferenceCaseResult(
                input_data=input_line.strip(),
                expected_output=expected_output.strip(),
                predicted_output=predicted_output,
                is_correct=is_correct,
                raw_engine_response={
                    **engine_response,
                    "start_time_ns": engine_response.get("start_time_ns", 0),
                    "end_time_ns": engine_response.get("end_time_ns", 0)
                },
                raw_power_response={
                    "base": power_base_response,
                    "active": power_active_response,
                },
            )
        except Exception:
            return None

    # ---------------------------
    # 並列制御ヘルパー
    # ---------------------------
    async def _execute_with_concurrency_limit(self, semaphore: asyncio.Semaphore, endpoint_url: str, input_text: str, expected_output: str) -> Optional[InferenceCaseResult]:
        async with semaphore:
            await asyncio.sleep(0.5)
            return await self._process_single_test_case(endpoint_url, input_text, expected_output)

    # ---------------------------
    # 集計メトリクス計算 (Average Gross Energy)
    # ---------------------------
    def _calculate_metrics(self, results: List[InferenceCaseResult]) -> TestRunMetrics:
        correct_predictions = sum(1 for r in results if r.is_correct)
        total_test_cases = len(results)
        accuracy = correct_predictions / total_test_cases if total_test_cases > 0 else 0.0

        total_latency_ns = 0
        total_net_power_watts = 0.0
        total_gross_energy_j = 0.0  # 総Grossエネルギー

        for r in results:
            try:
                start_ns = int(r.raw_engine_response.get("start_time_ns", 0))
                end_ns = int(r.raw_engine_response.get("end_time_ns", 0))
                total_latency_ns += (end_ns - start_ns)

                power_active_w = float(r.raw_power_response["active"].get("power_watts", "0.0"))
                power_base_w   = float(r.raw_power_response["base"].get("power_watts", "0.0"))
                net_power_w    = max(0.0, power_active_w - power_base_w)
                total_net_power_watts += net_power_w

                # Grossエネルギー計算（台形法）
                dt_s = (end_ns - start_ns) / 1_000_000_000
                avg_power_w = (power_active_w + power_base_w) / 2
                total_gross_energy_j += avg_power_w * dt_s
            except Exception:
                continue

        if total_test_cases == 0:
            return TestRunMetrics(
                accuracy=0.0,
                latency_ms=0.0,
                cost_estimate_mwh=0.0,
                cost_estimate_mj=0.0,
                average_gross_mj=0.0,
                total_test_cases=0,
                correct_predictions=0,
            )

        # 平均レイテンシ (ミリ秒)
        avg_latency_ms = (total_latency_ns / total_test_cases) / 1_000_000

        # 平均電力 (W) = Netベース
        avg_net_power_w = total_net_power_watts / total_test_cases
        avg_latency_s = avg_latency_ms / 1000

        # 既存コスト計算 (mWh, mJ)
        cost_estimate_mwh = avg_net_power_w * (avg_latency_s / 3600) * 1000
        cost_estimate_mj  = avg_net_power_w * avg_latency_s * 1000

        # 平均Grossエネルギー (mJ) = 総Grossをケース数で割る
        average_gross_mj = (total_gross_energy_j / total_test_cases) * 1000

        return TestRunMetrics(
            accuracy=accuracy,
            latency_ms=avg_latency_ms,
            cost_estimate_mwh=cost_estimate_mwh,
            cost_estimate_mj=cost_estimate_mj,
            average_gross_mj=average_gross_mj,
            total_test_cases=total_test_cases,
            correct_predictions=correct_predictions,
        )

    # ---------------------------
    # メイン: バッチテスト実行
    # ---------------------------
    async def run_batch_inference_test(self, test_file: UploadedFileStream, endpoint_url: str) -> DeploymentTestResult:
        file_bytes = await test_file.read()
        file_content = file_bytes.decode("utf-8").strip()
        
        # 2カラム（context\tpositive）と3カラム（context\tpositive\tnegative）の両方に対応
        test_data_pairs = []
        for line in file_content.split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 2:  # 2カラム以上あればOK
                input_text = parts[0]
                expected_output = parts[1]  # 2カラム目（positive）のみ使用、3カラム目は無視
                test_data_pairs.append((input_text, expected_output))

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENCY)
        tasks = [
            self._execute_with_concurrency_limit(semaphore, endpoint_url, input_text, expected_output)
            for input_text, expected_output in test_data_pairs
        ]

        case_results: List[Optional[InferenceCaseResult]] = await asyncio.gather(*tasks)
        valid_case_results = [r for r in case_results if r is not None]

        overall_metrics = self._calculate_metrics(valid_case_results)

        return DeploymentTestResult(
            overall_metrics=overall_metrics,
            case_results=valid_case_results,
        )
