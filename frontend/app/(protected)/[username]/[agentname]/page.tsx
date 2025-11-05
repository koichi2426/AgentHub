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
  getAgentFinetuningJobs, 
  FinetuningJobListItem, 
} from "@/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs"; 
// ▲▲▲ 修正ここまで ★★★ ▲▲▲

// ★★★ 修正1: Get Agent Deployments Fetcherと型をインポート ★★★
import { 
    getAgentDeployments, 
    DeploymentListItem, 
} from "@/fetchs/get_agent_deployments/get_agent_deployments";

import AgentTabFineTuning from "@/components/agent-tabs/agent-tab-finetuning";
import AgentTabDeployments from "@/components/agent-tabs/agent-tab-deployments";
import AgentTabSettings from "@/components/agent-tabs/agent-tab-settings";

import type { User, Agent, FinetuningJob, Deployment } from "@/lib/data"; 

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
  // ★★★ 修正2: Deployments の State を追加 ★★★
  const [agentDeployments, setAgentDeployments] = useState<DeploymentListItem[]>([]);
  
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
        // ... (省略: ユーザーとエージェントの取得・チェックロジック) ...
        const currentUser = await getUser(token);

        if (currentUser.username.toLowerCase() !== username.toLowerCase()) {
          notFound();
          return;
        }
        setUser(currentUser);

        const agentsResponse = await getUserAgents(token);
        
        const foundAgent = agentsResponse.agents.find(
          (a) =>
            a.owner.toLowerCase() === username.toLowerCase() &&
            a.name.toLowerCase() === agentname.toLowerCase()
        );

        if (!foundAgent) {
            notFound();
            return;
        }

        setAgent(foundAgent);

        // --- データ取得を並列化 ---
        const [jobsResponse, deploymentsResponse] = await Promise.all([
            getAgentFinetuningJobs(foundAgent.id, token), // Finetuning Jobs
            getAgentDeployments(foundAgent.id, token),      // ★★★ 修正3: Deployments を取得 ★★★
        ]);
        
        setFinetuningJobs(jobsResponse.jobs);
        setAgentDeployments(deploymentsResponse.deployments); // ★★★ 修正3: Stateにセット ★★★
        // ... (省略: データ取得のロジックはここまで) ...

      } catch (e) {
        console.error("Failed to fetch agent data:", e);
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

  // ... (省略: エラーチェックと notFound ロジック) ...

  if (error) {
     return (
        <div className="container mx-auto max-w-6xl p-4 md:p-10 text-center text-red-500">
            {error}
        </div>
    );
  }

  if (!user || !agent) {
    return notFound(); 
  }

  // --- AgentListItemをAgent型に変換 (下流コンポーネント互換性のため) ---
  const agentCasted = agent as unknown as Agent;
  const userCasted = user as unknown as User;

  // --- ジョブデータを下流コンポーネメントの型に合わせる ---
  const agentJobsCasted = finetuningJobs as unknown as FinetuningJob[]; 
  
  // ★★★ 修正4: デプロイメントデータを下流コンポーネントの型に合わせる ★★★
  const deploymentsCasted = agentDeployments as unknown as Deployment[]; 

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
          {/* ★★★ 修正5: 取得したデプロイメントデータを渡す ★★★ */}
          <AgentTabDeployments 
            deployments={deploymentsCasted} 
            username={user.username} 
            agentname={agent.name}
          />
        </TabsContent>

        {/* --- Settings タブ --- */}
        <TabsContent value="settings" className="mt-6">
          <AgentTabSettings agent={agentCasted} />
        </TabsContent>
      </Tabs>
    </div>
  );
}