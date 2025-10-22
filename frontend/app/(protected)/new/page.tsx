"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
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
import { Textarea } from "@/components/ui/textarea";
import { Bot } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { getUser, GetUserResponse } from "@/fetchs/get_user/get_user";
import { createAgent } from "@/fetchs/create_agent/create_agent"; // createAgentをインポート

export default function NewAgentPage() {
  const [user, setUser] = useState<GetUserResponse | null>(null);
  const [isUserLoading, setIsUserLoading] = useState(true); // ユーザー取得用のローディング
  const router = useRouter();

  // --- ▼▼▼ フォーム用の状態を追加 ▼▼▼ ---
  const [agentName, setAgentName] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false); // フォーム送信用のローディング
  const [error, setError] = useState<string | null>(null);
  // --- ▲▲▲ フォーム用の状態を追加 ▲▲▲ ---

  useEffect(() => {
    const fetchCurrentUser = async () => {
      const token = Cookies.get("auth_token");
      if (!token) {
        router.push("/login");
        return;
      }
      try {
        const userData = await getUser(token);
        setUser(userData);
      } catch (error) {
        console.error("Failed to fetch user", error);
        router.push("/login");
      } finally {
        setIsUserLoading(false);
      }
    };
    fetchCurrentUser();
  }, [router]);

  // --- ▼▼▼ フォーム送信ハンドラを追加 ▼▼▼ ---
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const token = Cookies.get("auth_token");
    if (!token || !user) {
      setError("Authentication error. Please log in again.");
      setIsSubmitting(false);
      return;
    }

    try {
      // APIを呼び出し
      const newAgent = await createAgent(
        { name: agentName, description: description || null },
        token
      );
      
      // 成功したら、作成したエージェントの所有者（自分）のページにリダイレクト
      router.push(`/${user.username}`);

    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };
  // --- ▲▲▲ フォーム送信ハンドラを追加 ▲▲▲ ---

  // ユーザー情報が読み込まれるまでローディング表示
  if (isUserLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading...
      </div>
    );
  }

  // userがnullの（useEffectでリダイレクトされるまでの）間
  if (!user) {
    return null;
  }

  return (
    <div className="container mx-auto max-w-3xl p-4 md:p-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Create a new Agent</h1>
        <p className="text-muted-foreground">
          An agent contains all the prompts, instructions, and configurations.
        </p>
      </div>

      <Card>
        {/* ▼▼▼ formタグで全体を囲み、onSubmitハンドラを設定 ▼▼▼ */}
        <form onSubmit={handleSubmit}>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Avatar className="mr-2 h-5 w-5">
                <AvatarImage src={user.avatar_url} />
                <AvatarFallback>
                  {user.name.substring(0, 1).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              {user.name}
              <span className="mx-2">/</span>
              {/* ▼▼▼ 入力中のエージェント名を動的に表示 ▼▼▼ */}
              <span className="font-normal text-muted-foreground">
                {agentName || "Agent name"}
              </span>
            </CardTitle>
            <CardDescription>
              Choose a name and provide a description for your new agent.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* フォームだったspace-y-6をdivに変更 */}
            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="agent-name">Agent name</Label>
                <Input
                  id="agent-name"
                  placeholder="My-Awesome-Agent"
                  required
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  disabled={isSubmitting}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (optional)</Label>
                <Textarea
                  id="description"
                  placeholder="A short description of what this agent does."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={isSubmitting}
                />
              </div>
              {/* エラーメッセージ表示欄 */}
              {error && <p className="text-sm text-destructive">{error}</p>}
            </div>
          </CardContent>
          <CardFooter>
            {/* ▼▼▼ ボタンのタイプをsubmitにし、ローディング状態を制御 ▼▼▼ */}
            <Button type="submit" disabled={isSubmitting}>
              <Bot className="mr-2 h-4 w-4" />
              {isSubmitting ? "Creating..." : "Create Agent"}
            </Button>
          </CardFooter>
        </form>
        {/* ▲▲▲ formタグで全体を囲む ▲▲▲ */}
      </Card>
    </div>
  );
}

