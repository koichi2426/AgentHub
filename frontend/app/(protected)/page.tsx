"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Bot } from "lucide-react";
import Link from "next/link";
import Cookies from "js-cookie";
import { getUser, GetUserResponse } from "../../fetchs/get_user/get_user";
import { getUserAgents, GetUserAgentsResponse } from "../../fetchs/get_user_agents/get_user_agents";
import { getAgents, GetAgentsResponse } from "../../fetchs/get_agents/get_agents";

export default function HomePage() {
  const [user, setUser] = useState<GetUserResponse | null>(null);
  const [userAgents, setUserAgents] = useState<GetUserAgentsResponse["agents"]>([]);
  const [allAgents, setAllAgents] = useState<GetAgentsResponse["agents"]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = Cookies.get("auth_token");
      if (!token) {
        setError("Please log in to continue.");
        setIsLoading(false);
        return;
      }

      try {
        const [userData, userAgentsData, allAgentsData] = await Promise.all([
          getUser(token),
          getUserAgents(token),
          getAgents(),
        ]);
        setUser(userData);
        setUserAgents(userAgentsData.agents);
        setAllAgents(allAgentsData.agents);
      } catch (err) {
        if (err instanceof Error) setError(err.message);
        else setError("An unknown error occurred.");
        Cookies.remove("auth_token");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen w-full bg-background text-foreground">
      <main className="container mx-auto p-4 md:p-6">
        <div className="grid gap-8 md:grid-cols-[240px_1fr]">
          {/* サイドバーエリア */}
          <aside className="hidden md:flex flex-col gap-4">
            {/* --- ▼ ユーザープロフィール表示エリア ▼ --- */}
            <div className="flex flex-col gap-3 items-center border rounded-lg p-4">
              {isLoading ? (
                <div className="w-full animate-pulse">
                  <div className="h-16 w-16 rounded-full bg-muted mx-auto"></div>
                  <div className="h-4 bg-muted rounded w-3/4 mt-3 mx-auto"></div>
                  <div className="h-3 bg-muted rounded w-1/2 mt-2 mx-auto"></div>
                </div>
              ) : error ? (
                <div className="text-center text-sm text-destructive">
                  <p>{error}</p>
                  <Link href="/login" className="font-bold underline hover:no-underline">
                    Login
                  </Link>
                </div>
              ) : user ? (
                <>
                  <Avatar className="w-16 h-16 border">
                    <AvatarImage src={user.avatar_url} alt={user.name} />
                    <AvatarFallback>{user.name.charAt(0).toUpperCase()}</AvatarFallback>
                  </Avatar>
                  <div className="text-center">
                    <h3 className="font-semibold">{user.name}</h3>
                    <p className="text-xs text-muted-foreground break-all">{user.email}</p>
                  </div>
                </>
              ) : null}
            </div>

            {/* --- ▼ ユーザーのエージェント一覧 ▼ --- */}
            <h2 className="font-semibold text-lg mt-4">Agents</h2>
            <Separator />
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : userAgents.length > 0 ? (
              userAgents.map((agent) => (
                <div key={agent.id} className="flex items-center gap-2 text-sm">
                  <Bot className="w-4 h-4 text-muted-foreground" />
                  {/* ✅ 修正部分：URLを /{owner}/{name} に */}
                  <Link
                    href={`/${agent.owner}/${agent.name}`}
                    className="hover:underline truncate"
                  >
                    {agent.owner}/{agent.name}
                  </Link>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No agents found.</p>
            )}
          </aside>

          {/* メインコンテンツエリア */}
          <div className="flex flex-col gap-6">
            <h1 className="text-2xl font-semibold">Home</h1>
            <Card>
              <CardHeader>
                <CardTitle>Feed</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4">
                  {isLoading ? (
                    <p className="text-sm text-muted-foreground">Loading feed...</p>
                  ) : allAgents.length > 0 ? (
                    allAgents.map((agent) => (
                      <li key={agent.id} className="border-b pb-4 last:border-b-0">
                        <div className="flex items-center gap-2">
                          <Bot className="w-4 h-4" />
                          <span className="text-xl font-bold text-blue-500 truncate">
                            {agent.owner}/{agent.name}
                          </span>
                        </div>
                        <p className="text-muted-foreground mt-2">
                          {agent.description}
                        </p>
                      </li>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No agents yet.</p>
                  )}
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
