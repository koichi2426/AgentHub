// frontend/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs.ts

import { API_URL } from "../config";

// ======================================
// Output DTO (バックエンドの GetAgentFinetuningJobsOutput に対応)
// ======================================

/**
 * バックエンドの FinetuningJobListItem DTO に対応する型
 */
export interface FinetuningJobListItem {
  id: number;
  agent_id: number;
  status: string;
  training_file_path: string;
  created_at: string; // ISO 8601 string
  finished_at: string | null; // ISO 8601 string or null
  error_message: string | null;
}

/**
 * バックエンドの GetAgentFinetuningJobsOutput に対応する最終的なレスポンス型
 */
export interface GetAgentFinetuningJobsResponse { // ★ クラス名を修正
  jobs: FinetuningJobListItem[];
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
 * 認証トークンを使用して、特定のAgentに紐づくファインチューニングジョブ一覧を取得する。
 * @param agentId 対象の Agent ID
 * @param token 認証トークン (Bearer)
 * @returns FinetuningJobListItem の配列を含むレスポンスオブジェクト
 */
export async function getAgentFinetuningJobs( // ★ 関数名を修正
  agentId: number, // ★ 引数に agentId を追加
  token: string
): Promise<GetAgentFinetuningJobsResponse> { // ★ Output DTO名を修正
  // ★★★ 修正: エンドポイントを /v1/jobs から /v1/agents/{agentId}/jobs に変更 ★★★
  const url = `${API_URL}/v1/agents/${agentId}/jobs`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json() as GetAgentFinetuningJobsResponse; // ★ Output DTO名を修正

  } catch (error) {
    console.error("Get Agent Finetuning Jobs Fetch Error:", error); // ★ ログの修正
    
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while fetching agent fine-tuning jobs."); // ★ エラーメッセージの修正
  }
}