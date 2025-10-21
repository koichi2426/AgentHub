// app/(protected)/layout.tsx
"use client";

import { useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { Header } from "@/components/header";
import { getUser, GetUserResponse } from "@/fetchs/get_user/get_user";

const AUTH_TOKEN_COOKIE_NAME = "auth_token";

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<GetUserResponse | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const token = Cookies.get(AUTH_TOKEN_COOKIE_NAME);
      if (token) {
        try {
          // トークンを使ってユーザー情報を取得
          const userData = await getUser(token);
          setUser(userData);
        } catch (error) {
          // トークンが無効ならクッキーを削除してログインページへ
          console.error("Authentication failed:", error);
          Cookies.remove(AUTH_TOKEN_COOKIE_NAME);
          router.push("/login");
        }
      } else {
        router.push("/login");
      }
    };

    fetchUser();
  }, [router]);

  // ユーザー情報が取得できるまでローディング画面を表示
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div>Loading...</div>
      </div>
    );
  }

  // ユーザー情報が取得できたら、Headerに渡してページ本体を表示
  return (
    <>
      <Header user={user} />
      {children}
    </>
  );
}

