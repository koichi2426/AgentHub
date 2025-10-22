import { API_URL } from "../config";

// ======================================
// リクエストデータ型 (ファイルとパスパラメータ)
// ======================================
export interface CreateFinetuningJobRequest {
  /** * アップロードするファイル。FileオブジェクトをFormDataに格納して送信します。
   */
  trainingFile: File;
  // agent_id は URL パスパラメータとして送信するため、このリクエストデータ型には含めない
}

// ======================================
// レスポンスデータ型 (バックエンドの CreateFinetuningJobOutput に対応)
// ======================================
export interface CreateFinetuningJobResponse {
  id: number;
  agent_id: number;
  status: string; // e.g., "queued"
  created_at: string; // JavaScriptのDateオブジェクトとして扱われることが多いが、APIからは文字列で受け取る
  message: string;
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
 * トレーニングデータファイルをアップロードし、ファインチューニングジョブをキューに投入する。
 * @param requestData - トレーニングファイルを含むリクエストデータ
 * @param agentId - ジョブを紐づけるエージェントのID (URLパスパラメータ)
 * @param token - ユーザー認証トークン
 * @returns ジョブがキューに投入されたことを示すレスポンス
 */
export async function createFinetuningJob(
  requestData: CreateFinetuningJobRequest,
  agentId: number,
  token: string
): Promise<CreateFinetuningJobResponse> {
  // POST /v1/agents/{agent_id}/finetuning エンドポイント
  const url = `${API_URL}/v1/agents/${agentId}/finetuning`;

  // ファイル送信には FormData を使用
  const formData = new FormData();
  
  // バックエンドのUploadFile引数名 'training_file' に合わせて File オブジェクトを追加
  // バックエンド: training_file: UploadFile = File(...)
  formData.append('training_file', requestData.trainingFile, requestData.trainingFile.name);

  try {
    const response = await fetch(url, {
      method: "POST", 
      headers: {
        // multipart/form-data を送信する場合、Content-Type ヘッダーは通常、
        // ブラウザに任せる (boundaryを自動生成させる) ため、設定しない。
        // "Content-Type": "multipart/form-data" は設定しない。
        "Authorization": `Bearer ${token}`,
      },
      // リクエストボディに FormData オブジェクトを直接含める
      body: formData,
    });

    if (!response.ok) {
      // エラーレスポンスをJSONとしてパース
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status} ${response.statusText}`);
    }
    
    // 成功レスポンス (201 Created または 202 Accepted) をパース
    return await response.json() as CreateFinetuningJobResponse;

  } catch (error) {
    console.error("Create Finetuning Job Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while submitting the fine-tuning job.");
  }
}