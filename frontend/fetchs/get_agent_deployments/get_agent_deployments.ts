// frontend/fetchs/get_agent_deployments/get_agent_deployments.ts

import { API_URL } from "../config";

// ======================================
// Output DTO (内部リスト用 - バックエンドの DeploymentListItem に対応)
// ======================================
export interface DeploymentListItem {
  /**
   * デプロイメントID
   */
  id: number;
  
  /**
   * 紐づく Finetuning Job ID
   */
  job_id: number;
  
  /**
   * デプロイメントのステータス (例: "active", "inactive", "pending")
   */
  status: string;
  
  /**
   * 予測エンドポイントURL
   */
  endpoint: string | null;
}

// ======================================
// レスポンスデータ型 (バックエンドの GetAgentDeploymentsOutput に対応)
// ======================================
export interface GetAgentDeploymentsResponse {
  /**
   * デプロイメントリスト
   */
  deployments: DeploymentListItem[];
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
 * 認証トークンとAgent IDを使用して、特定のAgentに紐づくデプロイメント一覧を取得する。
 * @param agentId 対象の Agent ID (URLパスパラメータ)
 * @param token ユーザー認証トークン
 * @returns DeploymentListItem の配列を含むレスポンスオブジェクト
 */
export async function getAgentDeployments(
  agentId: number,
  token: string
): Promise<GetAgentDeploymentsResponse> {
  // GET /v1/agents/{agent_id}/deployments エンドポイント
  const url = `${API_URL}/v1/agents/${agentId}/deployments`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      // GETリクエストのため Content-Type は不要
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }

    return await response.json() as GetAgentDeploymentsResponse;

  } catch (error) {
    console.error("Get Agent Deployments Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while fetching the agent deployments.");
  }
}