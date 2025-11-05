// frontend/fetchs/get_deployment_methods/get_deployment_methods.ts

import { API_URL } from "../config";

// ======================================
// リクエストデータ型 (なし)
// ======================================
// このAPIはリクエストボディを必要としません。
// job_id は URL パスパラメータとして送信します。
export interface GetDeploymentMethodsRequest {
  // (Empty)
}

// ======================================
// レスポンスデータ型 (バックエンドの Output DTO に対応)
// ======================================
// (Python: GetDeploymentMethodsOutput(methods=methods))
export interface GetDeploymentMethodsResponse {
  /**
   * C++エンジンが現在ロードしているメソッド（機能）の文字列リスト
   * (例: ["Optimize the route", "Provide safety and emergency support"])
   */
  methods: string[];
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
 * 特定のジョブIDに紐づくC++エンジンに問い合わせ、
 * 現在ロードされているメソッド（機能）の一覧を取得する。
 * @param jobId - 対象の Finetuning Job ID (URLパスパラメータ)
 * @param token - ユーザー認証トークン
 * @returns ロードされているメソッドの文字列リスト
 */
export async function getDeploymentMethods(
  jobId: number,
  token: string
): Promise<GetDeploymentMethodsResponse> {
  // GET /v1/jobs/{job_id}/methods エンドポイント
  const url = `${API_URL}/v1/jobs/${jobId}/methods`;

  try {
    const response = await fetch(url, {
      method: "GET", // ★ GETリクエスト
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      // body: (GETリクエストのためボディなし)
    });

    if (!response.ok) {
      // エラーレスポンスをJSONとしてパース (400, 401, 404 など)
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }
    
    // 成功レスポンス (200 OK) をパース
    return await response.json() as GetDeploymentMethodsResponse;

  } catch (error) {
    console.error("Get Deployment Methods Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while fetching the deployment methods.");
  }
}