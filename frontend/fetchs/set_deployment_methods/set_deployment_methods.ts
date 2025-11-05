// frontend/fetchs/set_deployment_methods/set_deployment_methods.ts

import { API_URL } from "../config";

// ======================================
// リクエストデータ型 (バックエンドの SetDeploymentMethodsRequest に対応)
// ======================================
// (Python: SetDeploymentMethodsRequest(methods: List[str]))
export interface SetDeploymentMethodsRequest {
  /**
   * 設定するメソッド（機能）の文字列リスト
   * (例: ["Optimize the route", "Provide safety and emergency support"])
   */
  methods: string[];
}

// ======================================
// レスポンスデータ型 (バックエンドの Output DTO に対応)
// ======================================
// (Python: SetDeploymentMethodsOutput(methods=methods))
export interface SetDeploymentMethodsResponse {
  /**
   * DBに保存されたメソッド（機能）の文字列リスト
   * (リクエストで送信したものがそのまま返ってくる想定)
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
 * 特定のジョブIDに紐づくデプロイメントのメソッド（機能）リストをDBに保存（上書き）する。
 * @param requestData - 設定するメソッドのリストを含むリクエストボディ
 * @param jobId - 対象の Finetuning Job ID (URLパスパラメータ)
 * @param token - ユーザー認証トークン
 * @returns 保存されたメソッドのリスト
 */
export async function setDeploymentMethods(
  requestData: SetDeploymentMethodsRequest,
  jobId: number,
  token: string
): Promise<SetDeploymentMethodsResponse> {
  // POST /v1/jobs/{job_id}/methods エンドポイント
  const url = `${API_URL}/v1/jobs/${jobId}/methods`;

  try {
    const response = await fetch(url, {
      method: "POST", // ★ POSTリクエスト
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json", // ★ JSONボディを送信
      },
      body: JSON.stringify(requestData), // ★ リクエストボディをJSON文字列化
    });

    if (!response.ok) {
      // エラーレスポンスをJSONとしてパース (400, 401, 404 など)
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }
    
    // 成功レスポンス (200 OK) をパース
    return await response.json() as SetDeploymentMethodsResponse;

  } catch (error) {
    console.error("Set Deployment Methods Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while setting the deployment methods.");
  }
}