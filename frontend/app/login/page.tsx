// src/app/login/page.tsx
"use client"; // フォームの状態管理とイベント処理のためクライアントコンポーネントにする

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Github } from "lucide-react";
import Link from "next/link";
import Cookies from "js-cookie";
import { authLogin } from "@/fetchs/auth_login/auth_login";

// 保護レイアウトで設定したクッキー名と同じ名前にしてください
const AUTH_TOKEN_COOKIE_NAME = "auth_token";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // APIを呼び出してトークンを取得
      const response = await authLogin({ email, password });
      
      // 取得したトークンをクッキーに保存
      Cookies.set(AUTH_TOKEN_COOKIE_NAME, response.token, {
        expires: 7,
        secure: false, // ← 修正: 開発環境でも動作するようにfalseに変更
        sameSite: "Lax", // ← 追加: CSRF対策としてLaxを設定
      });

      // ログイン成功後、ホームページにリダイレクト
      router.push("/");
      router.refresh(); // サーバーコンポーネントを再描画させるために追加

    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <Github className="mx-auto h-12 w-12" />
          <CardTitle className="text-2xl mt-4">Sign in to AgentHub</CardTitle>
          <CardDescription>
            Enter your credentials to access your account.
          </CardDescription>
        </CardHeader>
        {/* ▼ formタグで囲み、onSubmitイベントを設定 ▼ */}
        <form onSubmit={handleSubmit}>
          <CardContent>
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                />
              </div>
              <div className="grid gap-2">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  <Link
                    href="#"
                    className="ml-auto inline-block text-sm underline"
                  >
                    Forgot your password?
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              {/* エラーメッセージ表示領域 */}
              {error && <p className="text-sm text-red-500">{error}</p>}

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Signing in..." : "Sign in"}
              </Button>
            </div>
          </CardContent>
        </form>
        {/* ▲ formタグで囲み、onSubmitイベントを設定 ▲ */}
        <CardFooter className="flex justify-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="underline">
              Sign up
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}