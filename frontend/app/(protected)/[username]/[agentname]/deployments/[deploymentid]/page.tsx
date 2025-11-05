"use client";

import { useEffect, useState } from "react";
import { notFound, useRouter } from "next/navigation";
import Cookies from "js-cookie";

// Fetch 関連
import { getUser } from "@/fetchs/get_user/get_user";
import { getUserAgents, AgentListItem } from "@/fetchs/get_user_agents/get_user_agents";

// ★★★ 修正1: 既存の fetcher を新しいものに置き換え ★★★
import { getAgentFinetuningJobs } from "@/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs"; 
import type { FinetuningJobListItem } from "@/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs"; // ★ 型のインポート元も変更

import { getFinetuningJobDeployment, GetFinetuningJobDeploymentResponse } from "@/fetchs/get_finetuning_job_deployment/get_finetuning_job_deployment";
import { createFinetuningJobDeployment } from "@/fetchs/create_finetuning_job_deployment/create_finetuning_job_deployment";

// ★★★ 修正2: メソッド関連の型インポートを維持 ★★★
import { getDeploymentMethods, MethodListItemDTO } from "@/fetchs/get_deployment_methods/get_deployment_methods"; 
import { setDeploymentMethods } from "@/fetchs/set_deployment_methods/set_deployment_methods"; 

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
  // methods stateは MethodListItemDTO[] で正しい
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
        const [agentsRes] = await Promise.all([
          getUserAgents(token),
        ]);

        const foundAgent = agentsRes.agents.find(
          (a) => a.owner.toLowerCase() === username.toLowerCase() &&
                 a.name.toLowerCase() === agentname.toLowerCase()
        );
        if (!foundAgent) notFound();

        // ★★★ 修正3: Agent IDを使ってジョブ一覧を取得 ★★★
        const jobsRes = await getAgentFinetuningJobs(foundAgent.id, token);
        
        // ★★★ 修正4: Agentに紐づくジョブリストから deploymentid と一致するものを探す ★★★
        const foundJob = jobsRes.jobs.find(
          (j) => Number(j.id) === Number(deploymentid)
        );
        if (!foundJob) notFound();
        // ★★★ 修正ここまで ★★★

        if (
          foundAgent.owner.toLowerCase() !== username.toLowerCase() ||
          foundAgent.name.toLowerCase() !== agentname.toLowerCase()
        ) {
          notFound();
        }

        setAgentData(foundAgent);
        setJobData(foundJob);

        // --- Step 2: デプロイメント取得 or 自動作成 ---
        let deployment: GetFinetuningJobDeploymentResponse | null = null;
        try {
          deployment = await getFinetuningJobDeployment(Number(foundJob.id), token);
        } catch {
          console.warn("WARN: Deployment not found, creating new one...");
        }

        if (!deployment) {
          try {
            const created = await createFinetuningJobDeployment(Number(foundJob.id), token);
            // created.deployment は GetFinetuningJobDeploymentResponse と同じ構造ではないため、
            // 必要なプロパティだけを抽出してキャストします
            deployment = {
              id: created.deployment.id,
              finetuning_job_id: created.deployment.job_id,
              status: created.deployment.status,
              endpoint: created.deployment.endpoint,
            } as GetFinetuningJobDeploymentResponse;
            console.info("✅ Created new deployment:", deployment);
          } catch (createErr) {
            console.error("❌ Failed to create deployment:", createErr);
            throw new Error("Deployment not found and failed to create automatically.");
          }
        }

        setDeploymentData(deployment);

        // --- Step 3: メソッド一覧取得 ---
        try {
          const methodsRes = await getDeploymentMethods(Number(foundJob.id), token);
          setMethods(methodsRes.methods); 
        } catch (err) {
          console.warn("WARN: getDeploymentMethods failed, initializing defaults...");
          try {
            const setRes = await setDeploymentMethods(Number(foundJob.id), token);
            console.info("Default methods initialized:", setRes.methods);
            setMethods(setRes.methods); 
          } catch (setErr) {
            console.error("Failed to initialize methods:", setErr);
            setMethods([]);
          }
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
  const methodNames: string[] = methods.map(m => m.name); // nameプロパティを取り出す


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