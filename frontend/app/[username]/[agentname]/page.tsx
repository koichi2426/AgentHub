import { notFound } from "next/navigation";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Cpu, Rocket, Settings } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";

import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import jobs from "@/lib/mocks/finetuning_jobs.json";
import deployments from "@/lib/mocks/deployments.json";

import FineTuningUploader from "@/components/fine-tuning-uploader";
import JobHistoryTable from "@/components/job-history-table"; // ← 新規クライアントコンポーネント

export default async function AgentPage({
  params: rawParams,
}: {
  params:
    | { username: string; agentname: string }
    | Promise<{ username: string; agentname: string }>;
}) {
  // ★ params 非同期対応
  const resolvedParams = await Promise.resolve(rawParams);
  const { username, agentname } = resolvedParams;

  const lowerUsername = username.toLowerCase();
  const lowerAgentname = agentname.toLowerCase();

  // データ探索
  const user = users.find((u) => u.name.toLowerCase() === lowerUsername);
  const agent = agents.find(
    (a) =>
      a.owner.toLowerCase() === lowerUsername &&
      a.name.toLowerCase() === lowerAgentname
  );

  if (!user || !agent) notFound();

  const agentJobs = jobs.filter((job) => job.agentId === agent.id);
  const modelIds = [
    `model_${agent.name.toLowerCase().replace(/-/g, "")}_v1_base`,
    ...agentJobs.map((j) => j.modelId),
  ];
  const agentDeployments = deployments.filter((dep) =>
    modelIds.includes(dep.modelId)
  );

  return (
    <div className="container mx-auto max-w-6xl p-4 md:p-10">
      {/* Header */}
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

      {/* Tabs */}
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

        {/* Fine-tuning タブ */}
        <TabsContent value="finetuning" className="mt-6">
          {/* JSONLアップローダ */}
          <FineTuningUploader agentId={agent.id} />

          {/* Job 履歴テーブル */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Job History</CardTitle>
            </CardHeader>
            <CardContent>
              <JobHistoryTable
                jobs={agentJobs}
                username={user.name}
                agentname={agent.name}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Deployments タブ */}
        <TabsContent value="api" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Model Deployments</CardTitle>
              <CardDescription>
                Manage and test API endpoints for your fine-tuned models.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Model ID</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Endpoint</TableHead>
                    <TableHead className="text-center">Activate</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {agentDeployments.map((dep) => (
                    <TableRow key={dep.id}>
                      <TableCell className="font-mono font-medium">
                        {dep.modelId}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            dep.status === "active" ? "outline" : "secondary"
                          }
                        >
                          <span
                            className={`mr-2 h-2 w-2 rounded-full ${
                              dep.status === "active"
                                ? "bg-green-500"
                                : "bg-gray-500"
                            }`}
                          ></span>
                          {dep.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {dep.endpoint}
                      </TableCell>
                      <TableCell className="text-center">
                        <Switch checked={dep.status === "active"} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings タブ */}
        <TabsContent value="settings" className="mt-6">
          <p>Settings...</p>
        </TabsContent>
      </Tabs>
    </div>
  );
}
