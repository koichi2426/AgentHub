import { API_URL } from "../config";

// ======================================
// Output DTO: 画像バイナリを表現する Blob を返す
// ======================================
// Blob はブラウザで画像をレンダリングするための標準的なバイナリコンテナです

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
 * FastAPIのプロキシエンドポイントから、特定の可視化画像ストリームを直接取得する。
 * * NOTE: このプロキシは認証を要求しない前提で実装されています。
 * * @param relativePath VPSの可視化ベースディレクトリに対する相対パス (例: 'job_ID/layer0/image.png')
 * @returns 画像のバイナリデータを含む Blob オブジェクト
 */
export async function getImageStream(
  relativePath: string
): Promise<Blob> {
  // バックエンドのプロキシエンドポイントを使用
  // API_URL は 'http://localhost:8000' を想定
  const url = `${API_URL}/v1/visuals/${relativePath}`; 

  try {
    const response = await fetch(url, {
      method: "GET", 
      // プロキシエンドポイントは認証を要求しないため、headersは空
      headers: {},
    });

    if (!response.ok) {
      // 4xx や 5xx エラーが発生した場合
      
      // エラーレスポンスがJSON形式の場合（FastAPIが404, 500をJSONで返すため）
      try {
        const errorData: ApiError = await response.json();
        // エラーメッセージがあればそれを使用
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      } catch {
        // エラーレスポンスがJSONではない場合（例: プレーンテキストの404）
        throw new Error(`HTTP error! status: ${response.status} for URL: ${url}`);
      }
    }

    // 成功時、ResponseのバイナリボディをBlobとして変換し、返す
    // Blobには自動的にContent-Type (image/pngなど) が引き継がれます
    return await response.blob(); 

  } catch (error) {
    console.error(`Get Image Stream Fetch Error for path ${relativePath}:`, error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while fetching the image stream.");
  }
}
