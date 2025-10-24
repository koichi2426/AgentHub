import { API_URL } from "../config";

// ======================================
// Output DTO (バックエンドの GetUserFinetuningJobsOutput に対応)
// ======================================

/**
 * バックエンドの FinetuningJobListItem DTO に対応する型
 */
export interface FinetuningJobListItem {
  id: number;
  agent_id: number;
  status: string;
  training_file_path: string;
  model_id: string | null;
  created_at: string; // ISO 8601 string
  finished_at: string | null; // ISO 8601 string or null
  error_message: string | null;
}

/**
 * バックエンドの GetUserFinetuningJobsOutput に対応する最終的なレスポンス型
 */
export interface GetUserFinetuningJobsResponse {
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
 * 認証トークンを使用して、現在のユーザーが所有する全てのファインチューニングジョブ一覧を取得する。
 * @param token 認証トークン (Bearer)
 * @returns FinetuningJobListItem の配列を含むレスポンスオブジェクト
 */
export async function getUserFinetuningJobs(token: string): Promise<GetUserFinetuningJobsResponse> {
  const url = `${API_URL}/v1/jobs`; // GET /v1/jobs エンドポイントを使用

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
    return await response.json() as GetUserFinetuningJobsResponse;

  } catch (error) {
    console.error("Get User Finetuning Jobs Fetch Error:", error);
    
    // エラーが既に Error インスタンスであればそのままスロー
    if (error instanceof Error) {
      throw error;
    }
    // その他の予期せぬエラーの場合
    throw new Error("An unknown error occurred while fetching user fine-tuning jobs.");
  }
}