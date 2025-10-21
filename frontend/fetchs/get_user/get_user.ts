import { API_URL } from "../config";

// GETリクエストなので、リクエストボディの型定義は不要

export interface GetUserResponse {
  id: number; // バックエンドの型に合わせて修正
  username: string;
  name: string;
  email: string;
  avatar_url: string;
}

interface ApiError {
  error: string;
}

export async function getUser(token: string): Promise<GetUserResponse> {
  const url = `${API_URL}/v1/users/me`;

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
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();

  } catch (error) {
    console.error("Get User Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred while fetching user data.");
  }
}
