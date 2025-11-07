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
  // deploymentId は URL パスパラメータとして送信するため、このリクエストデータ型には含めない
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
  deploymentId: number, // ★ deploymentId に変更
  token: string
): Promise<TestDeploymentInferenceResponse> {
  // POST /v1/deployments/{deployment_id}/test エンドポイント
  const url = `${API_URL}/v1/deployments/${deploymentId}/test`; // ★ URLを修正

  // ファイル送信には FormData を使用
  const formData = new FormData();
  
  // バックエンドのUploadFile引数名 'test_file' に合わせて File オブジェクトを追加
  // バックエンド: test_file: UploadFile = File(...)
  formData.append('test_file', requestData.testFile, requestData.testFile.name); // ★ フィールド名を修正

  try {
    const response = await fetch(url, {
      method: "POST", 
      headers: {
        // multipart/form-data を送信する場合、Content-Type ヘッダーは設定しない。
        "Authorization": `Bearer ${token}`,
      },
      // リクエストボディに FormData オブジェクトを直接含める
      body: formData,
    });

    if (!response.ok) {
      // エラーレスポンスをJSONとしてパース
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }
    
    // 成功レスポンス (200 OK) をパース
    return await response.json() as TestDeploymentInferenceResponse;

  } catch (error) {
    console.error("Test Deployment Inference Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while submitting the deployment test.");
  }
}