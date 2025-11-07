# backend/infrastructure/domain/services/deployment_test_domain_service_impl.py

import asyncio
import json
import httpx # 非同期HTTPクライアント
import os
from typing import List, Dict, Any, Optional

# ドメイン層の依存関係
from domain.value_objects.file_data import UploadedFileStream
from domain.services.deployment_test_domain_service import DeploymentTestDomainService

# 定義済みの Value Object を正確にインポート
from domain.value_objects.deployment_test_result import DeploymentTestResult 
from domain.value_objects.inference_case_result import InferenceCaseResult
from domain.value_objects.test_run_metrics import TestRunMetrics


# === 外部APIのURL（仮） ===
POWER_API_URL = os.environ.get("POWER_MONITOR_API_URL", "http://localhost:8080/power") 


class DeploymentTestDomainServiceImpl(DeploymentTestDomainService):
    """
    デプロイメントテスト実行の具体的な実装。
    外部サービスに並列で問い合わせ、最終的な評価結果V.O.を構築する。
    """
    # ★★★ 修正箇所 1: 最大並列数を 1 に設定し、逐次実行を強制 ★★★
    MAX_CONCURRENCY = 1 

    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    def _extract_predicted_output(self, engine_response: Dict[str, Any]) -> str:
        """エンジンレスポンスから最も類似度の高い予測値（method）を抽出する。"""
        results = engine_response.get("results")
        if results and isinstance(results, list) and len(results) > 0:
            # 類似度が最も高い最初の要素の 'method' を返す
            return str(results[0].get("method", "")).strip()
        return ""

    async def _get_power_metrics(self) -> Dict[str, Any]:
        """外部の電力監視APIから瞬間の電力メトリクスを取得する。"""
        try:
            response = await self._client.get(POWER_API_URL, timeout=5)
            response.raise_for_status() 
            return response.json()
        except httpx.HTTPError as e:
            # 失敗した場合は、コスト計算がスキップされるようにエラーを示すダミーを返す
            return {"status": "error", "power_watts": "0.0", "timestamp_ns": "0"}

    async def _run_single_inference(self, endpoint_url: str, input_text: str) -> Dict[str, Any]:
        """単一の推論リクエストを外部エンジンに非同期で送信する。"""
        try:
            # ペイロードは {"prompt": "..."} で確定
            payload = {"prompt": input_text}
            response = await self._client.post(
                endpoint_url, 
                json=payload, 
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # 4xx/5xx エラーの場合は、エラー詳細をレスポンスに含めて返す
            error_message = f"Client error '{e.response.status_code} {e.response.reason_phrase}' for url '{endpoint_url}'"
            return {"status": "error", "error_detail": error_message, "results": []}
        except Exception as e:
            # 接続エラーなどの場合は、詳細を返す
            return {"status": "error", "error_detail": f"Connection Error: {str(e)}", "results": []}


    async def _process_single_test_case(self, endpoint_url: str, input_line: str, expected_output: str) -> Optional[InferenceCaseResult]:
        """単一のテストケースを実行し、InferenceCaseResult V.O. を構築する。"""
        try:
            # 1. 電力計測APIと推論リクエストを並列で実行
            power_future = self._get_power_metrics()
            inference_future = self._run_single_inference(endpoint_url, input_line)
            
            engine_response, power_response = await asyncio.gather(inference_future, power_future)
            
            # 2. 予測値の抽出と正誤判定
            predicted_output = self._extract_predicted_output(engine_response)
            
            # 正誤判定: 予測値が期待値と厳密に一致するかどうか
            is_correct = predicted_output.lower() == expected_output.lower() 
            
            # 3. InferenceCaseResult V.O. を構築
            return InferenceCaseResult(
                input_data=input_line.strip(),
                expected_output=expected_output.strip(),
                predicted_output=predicted_output,
                is_correct=is_correct,
                raw_engine_response=engine_response,
                raw_power_response=power_response
            )
            
        except Exception:
            # _process_single_test_case 内でCRITICALなエラーが発生した場合 (通常は上流でキャッチされる)
            return None 

    # ★★★ 修正箇所 2: セマフォを使用したタスク実行ヘルパーメソッド ★★★
    async def _execute_with_concurrency_limit(self, semaphore: asyncio.Semaphore, endpoint_url: str, input_text: str, expected_output: str) -> Optional[InferenceCaseResult]:
        """セマフォを利用して、_process_single_test_case の実行数を制限する。"""
        async with semaphore:
            # 修正：C++エンジンの負荷軽減のため、0.5秒の遅延を強制的に挿入
            await asyncio.sleep(0.5) 
            return await self._process_single_test_case(endpoint_url, input_text, expected_output)

    def _calculate_metrics(self, results: List[InferenceCaseResult]) -> TestRunMetrics:
        """個別の結果V.O.から、全体の評価メトリクスを計算する。"""
        
        correct_predictions = sum(1 for r in results if r.is_correct)
        total_test_cases = len(results)
        accuracy = correct_predictions / total_test_cases if total_test_cases > 0 else 0.0

        total_latency_ns = 0
        total_power_watts = 0.0
        
        for r in results:
            try:
                # 1. レイテンシ（ns）の計算
                start_ns = int(r.raw_engine_response.get("start_time_ns", 0))
                end_ns = int(r.raw_engine_response.get("end_time_ns", 0))
                total_latency_ns += (end_ns - start_ns)
                
                # 2. 電力（W）の加算
                power_w = float(r.raw_power_response.get("power_watts", "0.0"))
                total_power_watts += power_w
            except Exception:
                continue

        if total_test_cases == 0:
             return TestRunMetrics(accuracy=0.0, latency_ms=0.0, cost_estimate_mwh=0.0, total_test_cases=0, correct_predictions=0)

        # 3. 平均レイテンシ (ミリ秒)
        avg_latency_ms = (total_latency_ns / total_test_cases) / 1_000_000
        
        # 4. コスト計算 (mWh)
        avg_power_w = total_power_watts / total_test_cases
        avg_latency_s = avg_latency_ms / 1000
        cost_estimate_mwh = avg_power_w * avg_latency_s * 1000
        
        return TestRunMetrics(
            accuracy=accuracy,
            latency_ms=avg_latency_ms,
            cost_estimate_mwh=cost_estimate_mwh,
            total_test_cases=total_test_cases,
            correct_predictions=correct_predictions
        )


    async def run_batch_inference_test(
        self, 
        test_file: UploadedFileStream,
        endpoint_url: str,
    ) -> DeploymentTestResult:
        
        # 1. テストデータファイルの読み込みと整形
        file_bytes = await test_file.read() 
        file_content = file_bytes.decode('utf-8').strip()
        
        # 各行が "入力データ\t期待値" の形式を想定
        test_data_pairs = [line.split('\t', 1) for line in file_content.split('\n') if line.strip() and len(line.split('\t', 1)) == 2]
        
        # 2. 並列処理のためのタスク生成
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENCY)
        tasks = []
        for input_text, expected_output in test_data_pairs:
            tasks.append(
                self._execute_with_concurrency_limit(
                    semaphore, endpoint_url, input_text, expected_output
                )
            )
            
        # 3. 全てのタスクが完了するのを待つ (並列数を制限した実行)
        case_results: List[Optional[InferenceCaseResult]] = await asyncio.gather(*tasks)
        
        # 4. 失敗したケース (None) を除外
        valid_case_results = [r for r in case_results if r is not None]
        
        # 5. 全体のメトリクスを計算
        overall_metrics = self._calculate_metrics(valid_case_results)
        
        # 6. 最終 V.O. を構築して返す
        return DeploymentTestResult(
            overall_metrics=overall_metrics,
            case_results=valid_case_results
        )