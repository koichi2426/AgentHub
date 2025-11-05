"use client"; // クライアントコンポーネントに変換

import { useState, useEffect } from "react";
import { notFound, useRouter } from "next/navigation";
import Link from "next/link";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Cpu, Rocket, Settings } from "lucide-react";

// --- API Fetchers ---
import { getUser, GetUserResponse } from "@/fetchs/get_user/get_user";
import { getUserAgents, AgentListItem } from "@/fetchs/get_user_agents/get_user_agents";
import Cookies from "js-cookie";

// ▼▼▼ [修正] Finetuning Jobs Fetcherと型をインポート ★★★ ▼▼▼
import { 
  getAgentFinetuningJobs, // ★ 関数名を修正
  FinetuningJobListItem, 
} from "@/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs"; // ★ ファイルパスも修正が必要
// ▲▲▲ 修正ここまで ★★★ ▲▲▲

import AgentTabFineTuning from "@/components/agent-tabs/agent-tab-finetuning";
import AgentTabDeployments from "@/components/agent-tabs/agent-tab-deployments";
import AgentTabSettings from "@/components/agent-tabs/agent-tab-settings";

import type { User, Agent, FinetuningJob, Deployment } from "@/lib/data"; 
// NOTE: AgentListItem を FinetuningJob[] に変換して下流コンポーネントに渡します。

// ページパラメータ型
type Params = { username: string; agentname: string };


export default function AgentPage({
  params, 
}: {
  params: Params;
}) {
  const { username, agentname } = params;
  const router = useRouter();

  // Stateの定義
  const [user, setUser] = useState<GetUserResponse | null>(null);
  const [agent, setAgent] = useState<AgentListItem | null>(null);
  const [finetuningJobs, setFinetuningJobs] = useState<FinetuningJobListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null); // エラーハンドリング用

  useEffect(() => {
    const fetchAgentData = async () => {
      const token = Cookies.get("auth_token");
      if (!token) {
        router.push("/login"); 
        return;
      }

      try {
        // 1. ユーザー情報を取得
        const currentUser = await getUser(token);

        // 2. URLのユーザー名と認証済みユーザーが一致する場合は404
        if (currentUser.username.toLowerCase() !== username.toLowerCase()) {
          notFound();
          return;
        }
        setUser(currentUser);

        // 3. ユーザーのエージェント一覧を取得
        const agentsResponse = await getUserAgents(token);
        
        // 4. URL パラメータに一致するエージェントを検索
        const foundAgent = agentsResponse.agents.find(
          (a) =>
            a.owner.toLowerCase() === username.toLowerCase() &&
            a.name.toLowerCase() === agentname.toLowerCase()
        );

        // 5. エージェントが見つからなければ404
        if (!foundAgent) {
            notFound();
            return;
        }

        setAgent(foundAgent);

        // 6. ▼▼▼ [修正] ファインチューニングジョブ一覧を取得（Agent IDを渡す） ★★★ ▼▼▼
        // APIの責務が変更されたため、Agent IDを引数に渡し、フィルタリングはバックエンドに任せる
        const jobsResponse = await getAgentFinetuningJobs(foundAgent.id, token);
        
        // 7. クライアント側でのフィルタリングロジックを削除
        setFinetuningJobs(jobsResponse.jobs);
        // ▲▲▲ 修正ここまで ★★★ ▲▲▲

      } catch (e) {
        console.error("Failed to fetch agent data:", e);
        // エージェント情報だけでなく、ジョブ情報取得失敗もキャッチ
        setError("Failed to load agent or job details. Please check your network or token.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAgentData();
  }, [username, agentname, router]);


  // === ローディング・エラー状態の表示 ===
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading agent details...
      </div>
    );
  }

  // 認証済みだがデータ取得でエラーが発生した場合
  if (error) {
     return (
        <div className="container mx-auto max-w-6xl p-4 md:p-10 text-center text-red-500">
            {error}
        </div>
    );
  }

  // userまたはagentがnullの場合は notFound
  if (!user || !agent) {
    return notFound(); 
  }

  // --- AgentListItemをAgent型に変換 (下流コンポーネント互換性のため) ---
  const agentCasted = agent as unknown as Agent;
  const userCasted = user as unknown as User;

  // --- フィルタリングされたジョブデータを、既存の AgentTabFineTuning の型に合わせる ---
  // NOTE: ここでは FinetuningJobListItem[] を FinetuningJob[] としてキャストします
  const agentJobsCasted = finetuningJobs as unknown as FinetuningJob[]; 
  const agentDeployments: Deployment[] = []; // デプロイメントデータはAPI未実装のため空配列を維持

  // --- JSX 出力 ---
  return (
    <div className="container mx-auto max-w-6xl p-4 md:p-10">
      {/* --- ヘッダー --- */}
      <div className="mb-8">
        <h1 className="text-2xl font-normal">
          <Link href={`/${user.username}`} className="text-primary hover:underline">
            {user.username}
          </Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <span className="font-semibold">{agent.name}</span>
        </h1>
        <p className="mt-2 text-muted-foreground">{agent.description ?? "No description available."}</p>
      </div>

      {/* --- タブ --- */}
      <Tabs defaultValue="finetuning" className="w-full">
        <TabsList>
          <TabsTrigger value="finetuning">
            <Rocket className="mr-2 h-4 w-4" />
            Fine-tuning
          </TabsTrigger>
          <TabsTrigger value="api">
            <Cpu className="mr-2 h-4 w-4" />
            Deployments
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        {/* --- Fine-tuning タブ --- */}
        <TabsContent value="finetuning" className="mt-6">
          <AgentTabFineTuning user={userCasted} agent={agentCasted} jobs={agentJobsCasted} /> 
        </TabsContent>

        {/* --- Deployments タブ --- */}
        <TabsContent value="api" className="mt-6">
          <AgentTabDeployments deployments={agentDeployments} username={user.username} agentname={agent.name}/>
        </TabsContent>

        {/* --- Settings タブ --- */}
        <TabsContent value="settings" className="mt-6">
          <AgentTabSettings agent={agentCasted} />
        </TabsContent>
      </Tabs>
    </div>
  );
}