import { notFound } from "next/navigation";
import Link from "next/link";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Cpu, Rocket, Settings } from "lucide-react";

import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import rawJobs from "@/lib/mocks/finetuning_jobs.json";
import rawDeployments from "@/lib/mocks/deployments.json";

import AgentTabFineTuning from "@/components/agent-tabs/agent-tab-finetuning";
import AgentTabDeployments from "@/components/agent-tabs/agent-tab-deployments";
import AgentTabSettings from "@/components/agent-tabs/agent-tab-settings";

import type { User, Agent, FinetuningJob, Deployment } from "@/lib/data";

// ページパラメータ型
type Params = { username: string; agentname: string };

// JSON モックデータを厳密に型変換（status などを安全にキャスト）
const jobs: FinetuningJob[] = (rawJobs as unknown as FinetuningJob[]).map(
  (job) => ({
    ...job,
    status: job.status as "completed" | "running" | "failed",
    finishedAt: job.finishedAt ?? undefined,
  })
);

const deployments: Deployment[] = (
  rawDeployments as unknown as Deployment[]
).map((dep) => ({
  ...dep,
  status: dep.status as "active" | "inactive",
}));

export default async function AgentPage({
  params: rawParams,
}: {
  params: Params | Promise<Params>;
}) {
  const resolvedParams = await Promise.resolve(rawParams);
  const { username, agentname } = resolvedParams;

  const lowerUsername = username.toLowerCase();
  const lowerAgentname = agentname.toLowerCase();

  // --- 対応するユーザーとエージェントを検索 ---
  const user: User | undefined = (users as User[]).find(
    (u) => u.name.toLowerCase() === lowerUsername
  );

  const agent: Agent | undefined = (agents as Agent[]).find(
    (a) =>
      a.owner.toLowerCase() === lowerUsername &&
      a.name.toLowerCase() === lowerAgentname
  );

  if (!user || !agent) notFound();

  // --- エージェントに紐づくジョブとデプロイメントを抽出 ---
  const agentJobs: FinetuningJob[] = jobs.filter(
    (job) => job.agentId === agent.id
  );

  const modelIds = [
    `model_${agent.name.toLowerCase().replace(/-/g, "")}_v1_base`,
    ...agentJobs.map((j) => j.modelId),
  ];

  const agentDeployments: Deployment[] = deployments.filter((dep) =>
    modelIds.includes(dep.modelId)
  );

  // --- JSX 出力 ---
  return (
    <div className="container mx-auto max-w-6xl p-4 md:p-10">
      {/* --- ヘッダー --- */}
      <div className="mb-8">
        <h1 className="text-2xl font-normal">
          <Link href={`/${user.name}`} className="text-primary hover:underline">
            {user.name}
          </Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <span className="font-semibold">{agent.name}</span>
        </h1>
        <p className="mt-2 text-muted-foreground">{agent.description}</p>
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
          <AgentTabFineTuning user={user} agent={agent} jobs={agentJobs} />
        </TabsContent>

        {/* --- Deployments タブ --- */}
        <TabsContent value="api" className="mt-6">
          <AgentTabDeployments deployments={agentDeployments} username={user.name} agentname={agent.name}/>
        </TabsContent>

        {/* --- Settings タブ --- */}
        <TabsContent value="settings" className="mt-6">
          <AgentTabSettings agent={agent} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
