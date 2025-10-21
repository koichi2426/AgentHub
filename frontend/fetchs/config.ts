// frontend/fetchs/config.ts

// SSR (Node.js 側) か CSR (ブラウザ側) かを判定
const isServer = typeof window === "undefined";

let apiUrl: string;

if (isServer) {
  // サーバーサイドでの実行時
  apiUrl = process.env.API_URL_INTERNAL as string;
  if (!apiUrl) {
    // ビルド時やサーバーサイドでの実行時に環境変数がなければエラーを発生させる
    throw new Error("API_URL_INTERNAL is not defined. Please set it in your environment variables.");
  }
} else {
  // クライアントサイド（ブラウザ）での実行時
  apiUrl = process.env.NEXT_PUBLIC_API_URL as string;
  if (!apiUrl) {
    // ビルド時に環境変数がなければエラーを発生させる
    throw new Error("NEXT_PUBLIC_API_URL is not defined. Please set it in your environment variables.");
  }
}

export const API_URL = apiUrl;
