// frontend/fetchs/auth_login/auth_login.ts

import { API_URL } from "../config";

export interface AuthLoginRequest {
  email: string;
  password: string;
}

export interface AuthLoginResponse {
  token: string;
}

interface ApiError {
  error: string;
}

export async function authLogin(
  requestData: AuthLoginRequest
): Promise<AuthLoginResponse> {
  const url = `${API_URL}/v1/auth/login`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();

  } catch (error) {
    console.error("Auth Login Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred during login.");
  }
}