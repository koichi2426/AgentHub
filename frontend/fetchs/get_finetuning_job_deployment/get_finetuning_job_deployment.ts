// frontend/fetchs/get_finetuning_job_deployment/get_finetuning_job_deployment.ts

import { API_URL } from "../config";

// ======================================
// リクエストデータ型 (なし)
// ======================================
export interface GetFinetuningJobDeploymentRequest {
  // (Empty)
}

// ======================================
// レスポンスデータ型 (バックエンドの Output DTO に対応)
// ======================================
export interface GetFinetuningJobDeploymentResponse {
  id: number;
  finetuning_job_id: number; // Python Presenter の 'finetuning_job_id' に対応
  status: string;
  endpoint: string | null;
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
 * 特定のジョブIDに紐づくデプロイメントのステータス（エンドポイント等）を取得する。
 * @param jobId - 対象の Finetuning Job ID (URLパスパラメータ)
 * @param token - ユーザー認証トークン
 * @returns デプロイメントのステータス情報
 */
export async function getFinetuningJobDeployment(
  jobId: number,
  token: string
): Promise<GetFinetuningJobDeploymentResponse> {
  // GET /v1/jobs/{job_id}/deployment エンドポイント
  const url = `${API_URL}/v1/jobs/${jobId}/deployment`;

  try {
    const response = await fetch(url, {
      method: "GET", 
      headers: {
        "Authorization": `Bearer ${token}`,
        // ★ 修正: GETリクエストなので、Content-Typeは削除し、ヘッダーをクリーンにする ★
        // "Content-Type": "application/json", 
      },
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }
    
    return await response.json() as GetFinetuningJobDeploymentResponse;

  } catch (error) {
    console.error("Get Finetuning Job Deployment Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while fetching the deployment status.");
  }
}