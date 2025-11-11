// frontend/fetchs/test_deployment_inference/test_deployment_inference.ts

import { API_URL } from "../config";

// ======================================
// 内部DTO (バックエンドの V.O. に対応)
// ======================================

interface EngineResponseRaw {
  results: Array<{ method: string; similarity: string }>;
  start_time_ns: string;
  end_time_ns: string;
}

interface PowerResponseRaw {
  status: string;
  gpu_index: number;
  power_watts: string;
  timestamp_ns: string;
}

interface InferenceCaseResultDTO {
  id: number;
  input_data: string;
  expected_output: string;
  predicted_output: string;
  is_correct: boolean;
  raw_engine_response: EngineResponseRaw;
  raw_power_response: PowerResponseRaw;
}

interface TestRunMetricsDTO {
  accuracy: number;
  latency_ms: number;
  cost_estimate_mwh: number;
  cost_estimate_mj: number;
  gross_mj: number;
  total_test_cases: number;
  correct_predictions: number;
}

interface TestResultDTO {
  overall_metrics: TestRunMetricsDTO;
  case_results: InferenceCaseResultDTO[];
}

// ======================================
// リクエストデータ型 (ファイル)
// ======================================
export interface TestDeploymentInferenceRequest {
  /**
   * アップロードするテストデータファイル (.txt)。
   */
  testFile: File;
}

// ======================================
// レスポンスデータ型 (バックエンドの TestDeploymentInferenceOutput に対応)
// ======================================
export interface TestDeploymentInferenceResponse {
  test_result: TestResultDTO;
  message: string;
}

// ======================================
// エラーインターフェース
// ======================================
interface ApiError {
  error: string;
}

// ======================================
// Fetcher 関数
// ======================================

/**
 * テストデータファイルをアップロードし、デプロイされたモデルに対して推論テストを実行する。
 * @param requestData - テストファイルを含むリクエストデータ
 * @param deploymentId - テスト対象のデプロイメントID (URLパスパラメータ)
 * @param token - ユーザー認証トークン
 * @returns テスト結果（メトリクスと詳細ケース）を含むレスポンス
 */
export async function testDeploymentInference(
  requestData: TestDeploymentInferenceRequest,
  deploymentId: number,
  token: string
): Promise<TestDeploymentInferenceResponse> {
  const url = `${API_URL}/v1/deployments/${deploymentId}/test`;

  const formData = new FormData();
  formData.append("test_file", requestData.testFile, requestData.testFile.name);

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(
        errorData.error ||
          `HTTP error! status: ${response.status} ${response.statusText}`
      );
    }

    return (await response.json()) as TestDeploymentInferenceResponse;
  } catch (error) {
    console.error("Test Deployment Inference Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(
      "An unknown error occurred while submitting the deployment test."
    );
  }
}
