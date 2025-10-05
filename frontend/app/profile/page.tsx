import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Bot, GitBranch, Plus } from "lucide-react"; // Plusアイコンをインポート
import Link from "next/link";
import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import { Agent, User } from "@/lib/data";
import { Button } from "@/components/ui/button"; // Buttonコンポーネントをインポート

export default function ProfilePage() {
  // モックデータから特定のユーザーを取得（ここでは最初のユーザーを仮定）
  const user: User = users[0];

  // そのユーザーがオーナーのエージェントをフィルタリング
  const userAgents = agents.filter(
    (agent: Agent) => agent.owner === user.name
  );

  return (
    <div className="container mx-auto max-w-5xl p-10">
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

        {/* 右側: エージェント一覧 */}
        <div className="flex-1">
          {/* ↓↓ ここから下を修正しました ↓↓ */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Agents</h2>
            <Button asChild>
              <Link href="/new">
                <Plus className="mr-2 h-4 w-4" /> New Agent
              </Link>
            </Button>
          </div>
          {/* ↑↑ ここまで ↑↑ */}
          <Separator className="my-4" />
          <div className="space-y-4">
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
                  <p className="text-muted-foreground">{agent.description}</p>
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
        </div>
      </div>
    </div>
  );
}
