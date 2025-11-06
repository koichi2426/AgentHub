"use client";

import { useEffect, useState } from "react";
import { notFound, useRouter } from "next/navigation";
import Cookies from "js-cookie";

// Fetch 関連
import { getUser } from "@/fetchs/get_user/get_user";
import { getUserAgents, AgentListItem } from "@/fetchs/get_user_agents/get_user_agents";

// Agent Finetuning Jobs fetcher
import { getAgentFinetuningJobs } from "@/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs"; 
import type { FinetuningJobListItem } from "@/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs"; 

import { getFinetuningJobDeployment, GetFinetuningJobDeploymentResponse } from "@/fetchs/get_finetuning_job_deployment/get_finetuning_job_deployment";

// メソッド関連の型インポート
import { getDeploymentMethods, MethodListItemDTO } from "@/fetchs/get_deployment_methods/get_deployment_methods"; 

// UIコンポーネント
import DeploymentBreadcrumb from "@/components/deployments/DeploymentBreadcrumb";
import DeploymentDetailCard from "@/components/deployments/DeploymentDetailCard";
import DeploymentTestCard from "@/components/deployments/DeploymentTestCard";
import DeploymentDangerZone from "@/components/deployments/DeploymentDangerZone";
import DeploymentMethodsCard from "@/components/deployments/DeploymentMethodsCard";

import type { User, Agent, Deployment } from "@/lib/data";

type DeploymentDetailPageProps = {
  params: {
    username: string;
    agentname: string;
    deploymentid: string;
  };
};

export default function DeploymentDetailPage({ params }: DeploymentDetailPageProps) {
  const { username, agentname, deploymentid } = params;
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [agentData, setAgentData] = useState<AgentListItem | null>(null);
  const [jobData, setJobData] = useState<FinetuningJobListItem | null>(null);
  const [deploymentData, setDeploymentData] = useState<GetFinetuningJobDeploymentResponse | null>(null);
  const [methods, setMethods] = useState<MethodListItemDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDeploymentData = async () => {
      const token = Cookies.get("auth_token");
      if (!token) {
        router.push("/login");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // --- Step 0: 認証ユーザー取得 ---
        const currentUser = await getUser(token);
        if (currentUser.username.toLowerCase() !== username.toLowerCase()) {
          notFound();
          return;
        }
        setUser(currentUser);

        // --- Step 1: Agent & Job 確認 ---
        const agentsRes = await getUserAgents(token);
        
        const foundAgent = agentsRes.agents.find(
          (a) => a.owner.toLowerCase() === username.toLowerCase() &&
                 a.name.toLowerCase() === agentname.toLowerCase()
        );
        if (!foundAgent) notFound();

        // Agent IDを使ってジョブ一覧を取得
        const jobsRes = await getAgentFinetuningJobs(foundAgent.id, token);
        
        // Agentに紐づくジョブリストから deploymentid と一致するものを探す
        const foundJob = jobsRes.jobs.find(
          (j) => Number(j.id) === Number(deploymentid)
        );
        if (!foundJob) notFound();

        if (
          foundAgent.owner.toLowerCase() !== username.toLowerCase() ||
          foundAgent.name.toLowerCase() !== agentname.toLowerCase()
        ) {
          notFound();
        }

        setAgentData(foundAgent);
        setJobData(foundJob);

        // --- Step 2: デプロイメント取得 ---
        let deployment: GetFinetuningJobDeploymentResponse | null = null;
        try {
          // デプロイメントが存在しない場合はここでエラーがスローされる想定
          deployment = await getFinetuningJobDeployment(Number(foundJob.id), token);
        } catch {
          // デプロイメントが存在しない場合は、ここでnotFound()
          notFound(); 
          return;
        }
        
        setDeploymentData(deployment);

        // --- Step 3: メソッド一覧取得 ---
        try {
          const methodsRes = await getDeploymentMethods(Number(foundJob.id), token);
          setMethods(methodsRes.methods); 
        } catch (err) {
          console.warn("WARN: getDeploymentMethods failed, assuming empty list.");
          setMethods([]); 
        }
      } catch (e: unknown) {
        console.error("Failed to fetch deployment data:", e);
        let msg = "Failed to load deployment details.";
        if (e instanceof Error && e.message !== "NEXT_NOT_FOUND") msg = e.message;
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDeploymentData();
  }, [username, agentname, deploymentid, router]);

  // methods stateが MethodListItemDTO[] なので、DeploymentMethodsCardに渡す前に文字列配列に変換
  const methodNames: string[] = methods.map(m => m.name);


  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading deployment details...
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto max-w-4xl p-4 md:p-10 text-center text-red-500">
        Error: {error}
      </div>
    );
  }

  if (!user || !agentData || !deploymentData) {
    notFound(); 
    return null;
  }

  const agent: Agent = {
    id: agentData.id,
    name: agentData.name,
    owner: agentData.owner,
    description: agentData.description ?? "",
  };

  const deployment: Deployment = {
    id: deploymentData.id,
    job_id: deploymentData.finetuning_job_id,
    status: deploymentData.status as "active" | "inactive",
    endpoint: deploymentData.endpoint ?? "",
  };

  const handleDeleteDeployment = () => {
    console.log(`Deleting deployment: ${deployment.id}`);
    alert(`デプロイメント「${deployment.id}」を削除しました。(シミュレーション)`);
    router.push(`/${username}/${agentname}`);
  };

  return (
    <div className="container mx-auto max-w-4xl p-6">
      <DeploymentBreadcrumb
        user={user}
        agent={agent}
        deploymentId={String(deployment.id)}
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DeploymentDetailCard deployment={deployment} />
        </div>
        <DeploymentMethodsCard methods={methodNames} />
      </div>

      <DeploymentTestCard deploymentId={String(deployment.id)} />
      <DeploymentDangerZone
        deploymentId={String(deployment.id)}
        onDelete={handleDeleteDeployment}
      />
    </div>
  );
}