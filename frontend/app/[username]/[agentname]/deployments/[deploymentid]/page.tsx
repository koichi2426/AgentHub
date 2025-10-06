import { notFound } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Terminal } from "lucide-react";

import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import rawDeployments from "@/lib/mocks/deployments.json";

import type { Deployment, User, Agent } from "@/lib/data";

export default async function DeploymentDetailPage({
  params,
}: {
  params: {
    username: string;
    agentname: string;
    deploymentid: string;
  };
}) {
  const { username, agentname, deploymentid } = params;

  const lowerUsername = username.toLowerCase();
  const lowerAgentname = agentname.toLowerCase();

  // --- ユーザーとエージェントの検索 ---
  const user: User | undefined = (users as User[]).find(
    (u) => u.name.toLowerCase() === lowerUsername
  );

  const agent: Agent | undefined = (agents as Agent[]).find(
    (a) =>
      a.owner.toLowerCase() === lowerUsername &&
      a.name.toLowerCase() === lowerAgentname
  );

  if (!user || !agent) notFound();

  // --- デプロイメントデータを型安全に変換 ---
  const deployments: Deployment[] = (rawDeployments as unknown as Deployment[]).map((dep) => ({
    ...dep,
    status: dep.status === "active" || dep.status === "inactive" ? dep.status : "inactive",
  }));

  // --- 対象デプロイメントを検索 ---
  const deployment = deployments.find((d) => d.id === deploymentid);
  if (!deployment) notFound();

  // --- 表示 ---
  return (
    <div className="container mx-auto max-w-4xl p-6">
      {/* パンくず */}
      <div className="mb-6">
        <h1 className="text-2xl font-normal">
          <Link href={`/${user.name}`} className="text-primary hover:underline">
            {user.name}
          </Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <Link
            href={`/${user.name}/${agent.name}`}
            className="text-primary hover:underline"
          >
            {agent.name}
          </Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <span className="font-semibold">{deployment.id}</span>
        </h1>
      </div>

      {/* 詳細カード */}
      <Card>
        <CardHeader>
          <CardTitle>Deployment Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-y-2">
            <div className="text-sm text-muted-foreground">Model ID</div>
            <div className="font-mono">{deployment.modelId}</div>

            <div className="text-sm text-muted-foreground">Status</div>
            <div>
              <Badge
                variant={
                  deployment.status === "active" ? "outline" : "secondary"
                }
              >
                <span
                  className={`mr-2 h-2 w-2 rounded-full ${
                    deployment.status === "active"
                      ? "bg-green-500"
                      : "bg-gray-500"
                  }`}
                ></span>
                {deployment.status}
              </Badge>
            </div>

            <div className="text-sm text-muted-foreground">Endpoint</div>
            <div className="font-mono text-xs break-all">
              {deployment.endpoint}
            </div>

            <div className="text-sm text-muted-foreground">Created At</div>
            <div>{new Date(deployment.createdAt).toLocaleString()}</div>
          </div>

          {/* APIテストセクション */}
          <div className="pt-6">
            <h3 className="font-semibold mb-2">Test API</h3>
            <p className="text-sm text-muted-foreground mb-4">
              You can test the deployed endpoint using the API console below.
            </p>
            <Button variant="outline">
              <Terminal className="mr-2 h-4 w-4" /> Open API Console
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
