"use client";

import { useState, useEffect } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bot, BookUser, Plus } from "lucide-react";
import Link from "next/link";
import agents from "@/lib/mocks/agents.json";
import { notFound, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { getUser, GetUserResponse } from "@/fetchs/get_user/get_user";
import Cookies from "js-cookie";
import { Agent } from "@/lib/data"; // data.tsからAgent型をインポート

type UserProfilePageProps = {
  params: {
    username: string;
  };
};

export default function UserProfilePage({ params }: UserProfilePageProps) {
  const [user, setUser] = useState<GetUserResponse | null>(null);
  const [userAgents, setUserAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchUserData = async () => {
      const token = Cookies.get("auth_token");
      if (!token) {
        router.push("/login");
        return;
      }

      try {
        const currentUser = await getUser(token);

        if (currentUser.username.toLowerCase() !== params.username.toLowerCase()) {
          notFound();
          return;
        }

        setUser(currentUser);
        const foundUserAgents = agents.filter(
          (agent) => agent.owner === currentUser.username
        );
        setUserAgents(foundUserAgents);

      } catch (error) {
        console.error("Failed to fetch user data:", error);
        notFound();
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, [params.username, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading profile...
      </div>
    );
  }

  if (!user) {
    return notFound();
  }

  return (
    <div className="container mx-auto max-w-6xl p-4 md:p-10">
      <div className="flex flex-col gap-10 lg:flex-row lg:gap-12">
        <aside className="w-full lg:w-1/4">
          <div className="flex flex-col items-center text-center lg:items-start lg:text-left">
            <Avatar className="h-48 w-48 lg:h-64 lg:w-64">
              <AvatarImage src={user.avatar_url} alt={user.name} />
              <AvatarFallback>
                {user.name.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="mt-4">
              <h1 className="text-2xl font-bold">{user.name}</h1>
              <p className="text-muted-foreground">{user.email}</p>
            </div>
          </div>
        </aside>

        <div className="flex-1">
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-2 md:w-[200px]">
              <TabsTrigger value="overview">
                <BookUser className="mr-2 h-4 w-4" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="agents">
                <Bot className="mr-2 h-4 w-4" />
                Agents
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Welcome to {user.name}&apos;s Profile</CardTitle>
                  <CardDescription>
                    This is the overview page. More content will be added here
                    later.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p>
                    You can find a summary of user activities and featured
                    agents here.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="agents" className="mt-6">
              <div className="flex items-center justify-end">
                <Button asChild>
                  <Link href="/new">
                    <Plus className="mr-2 h-4 w-4" />
                    New
                  </Link>
                </Button>
              </div>
              <div className="mt-4 space-y-4">
                {userAgents.map((agent) => (
                  <Card key={agent.id}>
                    <CardHeader>
                      <div className="flex items-center gap-4">
                        <Bot className="h-6 w-6" />
                        <Link
                          href={`/${user.username}/${agent.name}`}
                          className="text-xl font-bold text-primary hover:underline"
                        >
                          {agent.name}
                        </Link>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground">
                        {agent.description}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

