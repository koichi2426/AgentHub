// src/app/signup/page.tsx

"use client"; // フォームの入力と状態管理のため、クライアントコンポーネントに設定

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
import { UserPlus } from "lucide-react";
import Link from "next/link";
import { authSignup, AuthSignupRequest } from "@/fetchs/auth_signup/auth_signup";

export default function SignupPage() {
  // --- ▼ 状態管理フックを追加 ▼ ---
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  // --- ▲ 状態管理フックを追加 ▲ ---

  // --- ▼ フォーム送信ハンドラを追加 ▼ ---
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    // パスワードの確認
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      setIsLoading(false);
      return;
    }

    const requestData: AuthSignupRequest = {
      username,
      name,
      email,
      // フォームにない avatar_url はここで仮の値を設定
      avatar_url: `https://placehold.co/128x128/E0E0E0/757575?text=${username.slice(0, 2).toUpperCase()}`,
      password,
    };

    try {
      await authSignup(requestData);
      // 成功した場合、ログインページにリダイレクト
      router.push("/login");
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
  // --- ▲ フォーム送信ハンドラを追加 ▲ ---

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <UserPlus className="mx-auto h-12 w-12" />
          <CardTitle className="text-2xl mt-4">Create an account</CardTitle>
          <CardDescription>
            Enter your information to get started with AgentHub.
          </CardDescription>
        </CardHeader>
        {/* --- ▼ formタグで囲み、onSubmitイベントを設定 ▼ --- */}
        <form onSubmit={handleSubmit}>
          <CardContent>
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="suzuki"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  placeholder="Agent Smith"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={isLoading}
                />
              </div>
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
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="confirm-password">Confirm Password</Label>
                <Input
                  id="confirm-password"
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              {/* エラーメッセージ表示領域 */}
              {error && <p className="text-sm text-red-500">{error}</p>}

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Creating account..." : "Create account"}
              </Button>
            </div>
          </CardContent>
        </form>
        {/* --- ▲ formタグで囲み、onSubmitイベントを設定 ▲ --- */}
        <CardFooter className="flex justify-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Already have an account?{" "}
            <Link href="/login" className="underline">
              Sign in
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}