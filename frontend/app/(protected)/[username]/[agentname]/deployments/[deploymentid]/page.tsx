"use client";

import { useMemo } from "react";
import { notFound, useRouter } from "next/navigation";
import type { Deployment, User, Agent } from "@/lib/data";

// モックデータのインポート
import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import rawDeployments from "@/lib/mocks/deployments.json";

// 分割したコンポーネントのインポート
import DeploymentBreadcrumb from "@/components/deployments/DeploymentBreadcrumb";
import DeploymentDetailCard from "@/components/deployments/DeploymentDetailCard";
import DeploymentTestCard from "@/components/deployments/DeploymentTestCard";
import DeploymentDangerZone from "@/components/deployments/DeploymentDangerZone";

export default function DeploymentDetailPage({
  params,
}: {
  params: {
    username: string;
    agentname: string;
    deploymentid: string;
  };
}) {
  const { username, agentname, deploymentid } = params;
  const router = useRouter();

  // useMemoフックに型注釈を追加して implicit 'any' エラーを解消
  const { user, agent, deployment } : {
    user: User | undefined;
    agent: Agent | undefined;
    deployment: Deployment | undefined;
  } = useMemo(() => {
    const lowerUsername = username.toLowerCase();
    const lowerAgentname = agentname.toLowerCase();

    const foundUser = (users as User[]).find((u) => u.name.toLowerCase() === lowerUsername);
    const foundAgent = (agents as Agent[]).find((a) => a.owner.toLowerCase() === lowerUsername && a.name.toLowerCase() === lowerAgentname);
    const foundDeployment = (rawDeployments as unknown as Deployment[]).find((d) => d.id === deploymentid);

    return { user: foundUser, agent: foundAgent, deployment: foundDeployment };
  }, [username, agentname, deploymentid]);

  if (!user || !agent || !deployment) {
    notFound();
  }

  const handleDeleteDeployment = () => {
    console.log(`Deleting deployment: ${deployment.id}`);
    alert(`デプロイメント「${deployment.id}」を削除しました。(シミュレーション)`);
    router.push(`/${username}/${agentname}`);
  };

  return (
    <div className="container mx-auto max-w-4xl p-6">
      <DeploymentBreadcrumb user={user} agent={agent} deploymentId={deployment.id} />
      <DeploymentDetailCard deployment={deployment} />
      <DeploymentTestCard deploymentId={deployment.id} />
      <DeploymentDangerZone deploymentId={deployment.id} onDelete={handleDeleteDeployment} />
    </div>
  );
}