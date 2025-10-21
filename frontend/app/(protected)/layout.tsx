// app/(protected)/layout.tsx
"use client"; // クッキーの読み取りとリダイレクトのため

import { useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie"; // インストールしたライブラリ

// ▼ 認証トークンが保存されているクッキー名を指定してください
const AUTH_TOKEN_COOKIE_NAME = "auth_token";

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  // null: チェック中, true: 認証OK, false: 認証NG
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    // クライアントサイドでクッキーをチェック
    const token = Cookies.get(AUTH_TOKEN_COOKIE_NAME);

    if (token) {
      // トークンがあれば認証OK
      setIsAuthenticated(true);
    } else {
      // トークンがなければ認証NG、ログインページへ
      setIsAuthenticated(false);
      router.push("/login");
    }
  }, [router]);

  // 1. チェック中 (isAuthenticated が null) の場合
  //    ローディング画面を表示し、ページのチラ見えを防ぐ
  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div>Loading...</div>
      </div>
    );
  }

  // 2. 認証OK (isAuthenticated が true) の場合
  //    ページ本体 (children) を表示
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // 3. 認証NG (isAuthenticated が false) の場合
  //    リダイレクトが実行されるまでの間、何も表示しない
  return null;
}