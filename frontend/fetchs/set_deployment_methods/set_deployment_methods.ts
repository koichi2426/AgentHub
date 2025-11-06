// frontend/fetchs/set_deployment_methods/set_deployment_methods.ts

import { API_URL } from "../config";

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
export interface SetDeploymentMethodsResponse {
  /**
   * 処理されたデプロイメントのID
   */
  deployment_id: number;
  
  /**
   * DBに保存されたメソッド（機能）のリスト
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
 * 特定のジョブIDに紐づくメソッド設定を実行する。
 * （バックエンド仕様に合わせ、POSTボディは空オブジェクト）
 * @param jobId - 対象の Finetuning Job ID (URLパスパラメータ)
 * @param token - ユーザー認証トークン
 * @returns 保存されたメソッドリスト
 */
export async function setDeploymentMethods(
  jobId: number,
  token: string
): Promise<SetDeploymentMethodsResponse> {
  const url = `${API_URL}/v1/jobs/${jobId}/methods`;

  try {
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }

    return await response.json() as SetDeploymentMethodsResponse;
  } catch (error) {
    console.error("Set Deployment Methods Fetch Error:", error);
    if (error instanceof Error) throw error;
    throw new Error("An unknown error occurred while setting the deployment methods.");
  }
}