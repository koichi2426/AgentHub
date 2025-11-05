// frontend/fetchs/create_finetuning_job_deployment/create_finetuning_job_deployment.ts

import { API_URL } from "../config";

// ======================================
// リクエストデータ型 (なし)
// ======================================
// このAPIはリクエストボディを必要としません。
// job_id は URL パスパラメータとして送信します。
export interface CreateFinetuningJobDeploymentRequest {
  // (Empty)
}

// ======================================
// レスポンスデータ型 (バックエンドの Output DTO に対応)
// ======================================
interface CreatedDeploymentDTO {
  id: number;
  job_id: number;
  status: string;       // (例: "inactive")
  endpoint: string | null; // (例: "http://.../job45/predict" または null)
}

export interface CreateFinetuningJobDeploymentResponse {
  deployment: CreatedDeploymentDTO;
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
 * 特定のジョブIDに基づいて、デプロイメント（エンドポイント情報）をDBに作成する。
 * (バックエンドの C++ Watcher への通知はこのAPIとは別に行われる前提)
 * * @param jobId - デプロイメントを作成する対象の Finetuning Job ID (URLパスパラメータ)
 * @param token - ユーザー認証トークン
 * @returns 作成されたデプロイメント情報
 */
export async function createFinetuningJobDeployment(
  jobId: number,
  token: string
): Promise<CreateFinetuningJobDeploymentResponse> {
  // POST /v1/jobs/{job_id}/deployment エンドポイント
  const url = `${API_URL}/v1/jobs/${jobId}/deployment`;

  // このAPIはリクエストボディ（FormDataやJSON）を必要としません。

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        // ボディが空の場合でも、認証情報は必要
        "Authorization": `Bearer ${token}`,
        // ボディが空なので Content-Type は設定しない
      },
      // body: (リクエストボディなし)
    });

    if (!response.ok) {
      // エラーレスポンスをJSONとしてパース (400, 401, 404, 409 FileExistsError など)
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }
    
    // 成功レスポンス (201 Created) をパース
    return await response.json() as CreateFinetuningJobDeploymentResponse;

  } catch (error) {
    console.error("Create Finetuning Job Deployment Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while creating the deployment.");
  }
}