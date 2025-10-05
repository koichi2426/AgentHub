import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bot, GitBranch, BookUser, Plus } from "lucide-react"; // Plusアイコンをインポート
import Link from "next/link";
import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import { User } from "@/lib/data"; // Agentの型はモックデータから推論されるため不要に
import { notFound } from "next/navigation";
import { Button } from "@/components/ui/button"; // Buttonをインポート

// ページのPropsの型を定義
type UserProfilePageProps = {
  params: {
    username: string;
  };
};

export default function UserProfilePage({ params }: UserProfilePageProps) {
  // URLのusernameパラメータを使って、モックデータから該当ユーザーを探す
  const user = users.find(
    (u: User) => u.name.toLowerCase() === params.username.toLowerCase()
  );

  // ユーザーが見つからない場合は404ページを表示
  if (!user) {
    notFound();
  }

  // そのユーザーがオーナーのエージェントをフィルタリング
  const userAgents = agents.filter((agent) => agent.owner === user.name);

  return (
    <div className="container mx-auto max-w-6xl p-4 md:p-10">
      <div className="flex flex-col gap-10 lg:flex-row lg:gap-12">
        {/* 左側: ユーザー情報 */}
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

        {/* 右側: タブコンテンツ */}
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

            {/* Overviewタブの内容 */}
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

            {/* Agentsタブの内容 */}
            <TabsContent value="agents" className="mt-6">
              {/* ↓↓ ここから下を追記・修正しました ↓↓ */}
              <div className="flex items-center justify-end">
                <Button asChild>
                  <Link href="/new">
                    <Plus className="mr-2 h-4 w-4" />
                    New
                  </Link>
                </Button>
              </div>
              <div className="mt-4 space-y-4">
              {/* ↑↑ ここまで ↑↑ */}
                {userAgents.map((agent) => (
                  <Card key={agent.id}>
                    <CardHeader>
                      <div className="flex items-center gap-4">
                        <Bot className="h-6 w-6" />
                        <Link
                          href="#"
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
                      <div className="mt-4 flex items-center space-x-4 text-sm text-muted-foreground">
                        <div className="flex items-center">
                          <GitBranch className="mr-1 h-4 w-4" />
                          <span>Version {agent.version}</span>
                        </div>
                      </div>
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

