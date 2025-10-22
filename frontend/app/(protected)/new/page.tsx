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

export default function NewAgentPage() {
  const [user, setUser] = useState<GetUserResponse | null>(null);
  const router = useRouter();

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
        // トークンが無効な場合などもログインページにリダイレクト
        router.push("/login");
      }
    };
    fetchCurrentUser();
  }, [router]);

  // ユーザー情報が読み込まれるまでローディング表示
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading...
      </div>
    );
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
            <span className="font-normal text-muted-foreground">Agent name</span>
          </CardTitle>
          <CardDescription>
            Choose a name and provide a description for your new agent.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="agent-name">Agent name</Label>
              <Input
                id="agent-name"
                placeholder="My-Awesome-Agent"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                placeholder="A short description of what this agent does."
              />
            </div>
          </form>
        </CardContent>
        <CardFooter>
          <Button>
            <Bot className="mr-2 h-4 w-4" /> Create Agent
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
