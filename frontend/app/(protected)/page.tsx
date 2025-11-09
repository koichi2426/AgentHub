"use client";

import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { getUser, GetUserResponse } from "@/fetchs/get_user/get_user";
import { getUserAgents, GetUserAgentsResponse } from "@/fetchs/get_user_agents/get_user_agents";
import { getAgents, GetAgentsResponse } from "@/fetchs/get_agents/get_agents";
import { UserProfileCard } from "@/components/home/UserProfileCard";
import { UserAgentsList } from "@/components/home/UserAgentsList";
import { FeedCard } from "@/components/home/FeedCard";

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
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
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
          {/* サイドバー */}
          <aside className="hidden md:flex flex-col gap-4">
            <UserProfileCard isLoading={isLoading} error={error} user={user} />
            <UserAgentsList isLoading={isLoading} agents={userAgents} />
          </aside>

          {/* メイン */}
          <div className="flex flex-col gap-6">
            <h1 className="text-2xl font-semibold">Home</h1>
            <FeedCard isLoading={isLoading} agents={allAgents} />
          </div>
        </div>
      </main>
    </div>
  );
}
