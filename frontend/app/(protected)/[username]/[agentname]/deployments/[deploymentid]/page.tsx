"use client";

import { useMemo } from "react";
import { notFound, useRouter } from "next/navigation";
import type { Deployment, User, Agent, DeploymentMethodsEntry } from "@/lib/data";

// モックデータのインポート
import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import rawDeployments from "@/lib/mocks/deployments.json";
import rawMethods from "@/lib/mocks/methods.json"; 

// 分割したコンポーネントのインポート
import DeploymentBreadcrumb from "@/components/deployments/DeploymentBreadcrumb";
import DeploymentDetailCard from "@/components/deployments/DeploymentDetailCard";
import DeploymentTestCard from "@/components/deployments/DeploymentTestCard";
import DeploymentDangerZone from "@/components/deployments/DeploymentDangerZone";
import DeploymentMethodsCard from "@/components/deployments/DeploymentMethodsCard"; 

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

  const { user, agent, deployment, methods } : {
    user: User | undefined;
    agent: Agent | undefined;
    deployment: Deployment | undefined;
    methods: string[]; 
  } = useMemo(() => {
    const lowerUsername = username.toLowerCase();
    const lowerAgentname = agentname.toLowerCase();

    const foundUser = (users as User[]).find((u) => u.name.toLowerCase() === lowerUsername);
    const foundAgent = (agents as Agent[]).find((a) => a.owner.toLowerCase() === lowerUsername && a.name.toLowerCase() === lowerAgentname);
    
    // NOTE: Deployment型のフィールド名はスネークケースに修正済みと仮定
    const foundDeployment = (rawDeployments as unknown as Deployment[]).find((d) => d.id === deploymentid);
    
    // ★★★ 修正1: メソッドデータを検索 (インポートした DeploymentMethodsEntry を使用) ★★★
    const allMethods = rawMethods as DeploymentMethodsEntry[];
    const methodEntry = allMethods.find((m) => m.deploymentId === deploymentid);
    
    const methodList = methodEntry ? methodEntry.methods : [];


    return { user: foundUser, agent: foundAgent, deployment: foundDeployment, methods: methodList };
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
      
      {/* ★★★ レイアウトとメソッドカードの描画 ★★★ */}
      <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <DeploymentDetailCard deployment={deployment} />
          </div>
          <DeploymentMethodsCard methods={methods} /> 
      </div>
      
      <DeploymentTestCard deploymentId={deployment.id} />
      <DeploymentDangerZone deploymentId={deployment.id} onDelete={handleDeleteDeployment} />
    </div>
  );
}