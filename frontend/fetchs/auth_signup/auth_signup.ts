// frontend/fetchs/auth_signup/auth_signup.ts

import { API_URL } from "../config";

export interface AuthSignupRequest {
  username: string;
  name: string;
  email: string;
  avatar_url: string;
  password: string;
}

export interface AuthSignupResponse {
  id: string;
  username: string;
  name: string;
  email: string;
  avatar_url: string;
}

interface ApiError {
  error: string;
}

export async function authSignup(
  requestData: AuthSignupRequest
): Promise<AuthSignupResponse> {
  const url = `${API_URL}/v1/auth/signup`;

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
    console.error("Auth Signup Fetch Error:", error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unknown error occurred during signup.");
  }
}