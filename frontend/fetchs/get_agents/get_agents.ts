import { API_URL } from "../config";

// ======================================
// Output DTO (バックエンドの GetAgentsOutput に対応)
// ======================================

/**
 * バックエンドの AgentListItem DTO に対応する型
 */
export interface AgentListItem {
  id: number;
  user_id: number;
  owner: string;
  name: string;
  // description は Optional[str] に対応し、null を許容
  description: string | null; 
}

/**
 * バックエンドの GetAgentsOutput に対応する最終的なレスポンス型
 */
export interface GetAgentsResponse {
  agents: AgentListItem[];
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
 * 現存する全てのアクティブなエージェント一覧を取得する。
 * (このAPIは認証を必要としない)
 * * @returns AgentListItem の配列を含むレスポンスオブジェクト
 */
export async function getAgents(): Promise<GetAgentsResponse> {
  // GET /v1/agents/all エンドポイント (認証不要)
  const url = `${API_URL}/v1/agents/all`;

  try {
    const response = await fetch(url, {
      method: "GET", // GETリクエスト
      headers: {
        "Content-Type": "application/json",
      },
      // 認証トークンやbodyは不要
    });

    if (!response.ok) {
      // エラーレスポンスをJSONとしてパース
      const errorData: ApiError = await response.json();
      // エラーメッセージがあればそれを使用し、なければ一般的なHTTPエラーメッセージを使用
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    // 成功レスポンスをJSONとしてパースし、型を保証して返す
    return await response.json() as GetAgentsResponse;

  } catch (error) {
    console.error("Get All Agents Fetch Error:", error);
    
    // エラーが既に Error インスタンスであればそのままスロー
    if (error instanceof Error) {
      throw error;
    }
    // その他の予期せぬエラーの場合
    throw new Error("An unknown error occurred while fetching all agents data.");
  }
}