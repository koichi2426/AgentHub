import { API_URL } from "../config";

// APIに送信するリクエストデータの型
export interface CreateAgentRequest {
  name: string;
  description?: string | null;
}

// APIから返ってくるレスポンスデータの型
export interface CreateAgentResponse {
  id: number;
  user_id: number;
  owner: string;
  name: string;
  description: string | null;
}

interface ApiError {
  error: string;
}

export async function createAgent(
  requestData: CreateAgentRequest,
  token: string
): Promise<CreateAgentResponse> {
  const url = `${API_URL}/v1/agents`;

  try {
    const response = await fetch(url, {
      method: "POST", // POSTリクエスト
      headers: {
        "Content-Type": "application/json",
        // BearerトークンをAuthorizationヘッダーに含める
        "Authorization": `Bearer ${token}`,
      },
      // リクエストボディにエージェント情報をJSON化して含める
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();

  } catch (error) {
    console.error("Create Agent Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while creating the agent.");
  }
}
