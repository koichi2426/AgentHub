// src/app/page.tsx

import { Header } from "@/components/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import agents from "@/lib/mocks/agents.json";
// 不要なアイコン (Lock, Share2) と Badge を import から削除
import { Bot } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen w-full bg-background text-foreground">
      <main className="container mx-auto p-4 md:p-6">
        <div className="grid gap-8 md:grid-cols-[240px_1fr]">
          {/* サイドバーエリア */}
          <aside className="hidden md:flex flex-col gap-4">
            <h2 className="font-semibold text-lg">Agents</h2>
            <Separator />
            {agents.map((agent) => (
              <div key={agent.id} className="flex items-center gap-2 text-sm">
                {/* Public/Private の区別をなくし、Bot アイコンに統一 */}
                <Bot className="w-4 h-4 text-muted-foreground" />
                <Link href="#" className="hover:underline truncate">
                  {agent.owner}/{agent.name}
                </Link>
              </div>
            ))}
          </aside>

          {/* メインコンテンツエリア */}
          <div className="flex flex-col gap-6">
            <h1 className="text-2xl font-semibold">Home</h1>
            <Card>
              <CardHeader>
                <CardTitle>Your Agents</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4">
                  {agents.map((agent) => (
                    <li key={agent.id} className="border-b pb-4 last:border-b-0">
                      <div className="flex items-center gap-2">
                        {/* Public/Private の区別をなくし、Bot アイコンに統一 */}
                        <Bot className="w-4 h-4"/>
                        <Link href="#" className="text-xl font-bold text-blue-500 hover:underline">
                          {agent.name}
                        </Link>
                        {/* Public/Private の Badge を削除 */}
                      </div>
                      <p className="text-muted-foreground mt-2">{agent.description}</p>
                      {/* タグ表示エリアを削除 */}
                      {/* メタデータ表示をバージョンのみに簡素化 */}
                      <div className="flex items-center gap-4 text-sm mt-3 text-muted-foreground">
                        <span>v{agent.version}</span>
                        {/* シェア数表示を削除 */}
                      </div>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

