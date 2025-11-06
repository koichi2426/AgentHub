// frontend/fetchs/get_deployment_methods/get_deployment_methods.ts

import { API_URL } from "../config";

// ======================================
// リクエストデータ型
// ======================================
export interface GetDeploymentMethodsRequest {}

// ======================================
// 内部DTO
// ======================================
export interface MethodListItemDTO {
  /**
   * メソッド名（機能の文字列）
   */
  name: string;
}

// ======================================
// レスポンスデータ型
// ======================================
export interface GetDeploymentMethodsResponse {
  /**
   * 処理されたデプロイメントのID
   */
  deployment_id: number;
  
  /**
   * DBに保存されているメソッド（機能）のリスト
   */
  methods: MethodListItemDTO[];
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
 * 特定のジョブIDに紐づくデプロイメントのメソッド設定をDBから取得する。
 * @param jobId - 対象の Finetuning Job ID (URLパスパラメータ)
 * @param token - ユーザー認証トークン
 * @returns デプロイメントIDとメソッドのリスト
 */
export async function getDeploymentMethods(
  jobId: number,
  token: string
): Promise<GetDeploymentMethodsResponse> {
  const url = `${API_URL}/v1/jobs/${jobId}/methods`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }
    
    return await response.json() as GetDeploymentMethodsResponse;

  } catch (error) {
    console.error("Get Deployment Methods Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while fetching the deployment methods.");
  }
}