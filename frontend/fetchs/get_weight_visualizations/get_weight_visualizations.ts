import { API_URL } from "../config";

// ======================================
// Output DTO (バックエンドの GetFinetuningJobVisualizationOutput に対応)
// ======================================

/**
 * 可視化画像のURL詳細
 */
export interface WeightVisualizationDetail {
  name: string;
  before_url: string;
  after_url: string;
  delta_url: string;
}

/**
 * レイヤーごとの可視化データのリスト項目
 */
export interface LayerVisualizationOutput {
  layer_name: string;
  weights: WeightVisualizationDetail[];
}

/**
 * 可視化データ全体の最終的なレスポンス型
 */
export interface GetWeightVisualizationsResponse {
  job_id: number;
  layers: LayerVisualizationOutput[];
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
 * 認証トークンとジョブIDを使用して、特定のジョブの重み可視化データ一覧を取得する。
 * @param token 認証トークン (Bearer)
 * @param jobId 取得対象のファインチューニングジョブID
 * @returns 可視化データの構造を含むレスポンスオブジェクト
 */
export async function getWeightVisualizations(
  token: string,
  jobId: string | number
): Promise<GetWeightVisualizationsResponse> {
  const url = `${API_URL}/v1/jobs/${jobId}/visualizations`; // GET /v1/jobs/{job_id}/visualizations

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
    return (await response.json()) as GetWeightVisualizationsResponse;

  } catch (error) {
    console.error(`Get Weight Visualizations Fetch Error for job ${jobId}:`, error);

    // エラーが既に Error インスタンスであればそのままスロー
    if (error instanceof Error) {
      throw error;
    }
    // その他の予期せぬエラーの場合
    throw new Error("An unknown error occurred while fetching weight visualizations.");
  }
}
