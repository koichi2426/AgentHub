import { API_URL } from "../config";

// ======================================
// Output DTO (バックエンドの GetUserAgentsOutput に対応)
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
 * バックエンドの GetUserAgentsOutput に対応する最終的なレスポンス型
 */
export interface GetUserAgentsResponse {
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
 * 認証トークンを使用して、現在のユーザーが作成した全てのエージェント一覧を取得する。
 * * @param token 認証トークン (Bearer)
 * @returns AgentListItem の配列を含むレスポンスオブジェクト
 */
export async function getUserAgents(token: string): Promise<GetUserAgentsResponse> {
  const url = `${API_URL}/v1/agents`; // GET /v1/agents エンドポイント

  try {
    const response = await fetch(url, {
      method: "GET", // GETリクエスト
      headers: {
        "Content-Type": "application/json",
        // BearerトークンをAuthorizationヘッダーに含める
        "Authorization": `Bearer ${token}`,
      },
      // GETリクエストなのでbodyは不要
    });

    if (!response.ok) {
      // エラーレスポンスをJSONとしてパース
      const errorData: ApiError = await response.json();
      // エラーメッセージがあればそれを使用し、なければ一般的なHTTPエラーメッセージを使用
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    // 成功レスポンスをJSONとしてパースし、型を保証して返す
    return await response.json() as GetUserAgentsResponse;

  } catch (error) {
    console.error("Get User Agents Fetch Error:", error);
    
    // エラーが既に Error インスタンスであればそのままスロー
    if (error instanceof Error) {
      throw error;
    }
    // その他の予期せぬエラーの場合
    throw new Error("An unknown error occurred while fetching user agents data.");
  }
}