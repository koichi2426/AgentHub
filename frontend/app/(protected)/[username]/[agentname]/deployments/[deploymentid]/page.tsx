"use client";

import { useEffect, useState } from "react";
import { notFound, useRouter } from "next/navigation";
import Cookies from "js-cookie";

// Fetch 関連
import { getUser } from "@/fetchs/get_user/get_user";
import { getUserAgents, AgentListItem } from "@/fetchs/get_user_agents/get_user_agents";
import { getUserFinetuningJobs, FinetuningJobListItem } from "@/fetchs/get_user_finetuning_jobs/get_user_finetuning_jobs";
import { getFinetuningJobDeployment, GetFinetuningJobDeploymentResponse } from "@/fetchs/get_finetuning_job_deployment/get_finetuning_job_deployment";
import {
  setDeploymentMethods,
  SetDeploymentMethodsRequest,
} from "@/fetchs/set_deployment_methods/set_deployment_methods";
import { getDeploymentMethods } from "@/fetchs/get_deployment_methods/get_deployment_methods";

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
  const [methods, setMethods] = useState<string[]>([]);
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
        const [agentsRes, jobsRes] = await Promise.all([
          getUserAgents(token),
          getUserFinetuningJobs(token),
        ]);

        const foundJob = jobsRes.jobs.find((j) => Number(j.id) === Number(deploymentid));
        if (!foundJob) notFound();

        const foundAgent = agentsRes.agents.find(
          (a) => Number(a.id) === Number(foundJob!.agent_id)
        );
        if (!foundAgent) notFound();

        if (
          foundAgent.owner.toLowerCase() !== username.toLowerCase() ||
          foundAgent.name.toLowerCase() !== agentname.toLowerCase()
        ) {
          notFound();
        }

        setAgentData(foundAgent);
        setJobData(foundJob);

        // --- Step 2: デプロイ情報取得 ---
        let deployment: GetFinetuningJobDeploymentResponse | null = null;
        try {
          deployment = await getFinetuningJobDeployment(Number(foundJob.id), token);
        } catch {
          console.warn("WARN: Deployment not found, creating new one...");
        }

        // --- Step 3: 存在しない場合はデフォルトメソッドで作成 ---
        if (!deployment) {
          const defaultMethods: string[] = [
            "Optimize the route",
            "Provide safety and emergency support",
          ];
          const setReq: SetDeploymentMethodsRequest = { methods: defaultMethods };
          await setDeploymentMethods(setReq, Number(foundJob.id), token);
          deployment = await getFinetuningJobDeployment(Number(foundJob.id), token);
        }

        setDeploymentData(deployment!);

        // --- Step 4: メソッド一覧取得（別APIから） ---
        try {
          const methodsRes = await getDeploymentMethods(Number(foundJob.id), token);
          setMethods(methodsRes.methods);
        } catch (err) {
          console.warn("WARN: getDeploymentMethods failed, using defaults.");
          setMethods(["Optimize the route", "Provide safety and emergency support"]);
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
    id: agentData.id, // ✅ number型で統一
    name: agentData.name,
    owner: agentData.owner,
    description: agentData.description ?? "", // ✅ null安全
  };

  const deployment: Deployment = {
    id: deploymentData.id, // ✅ number型で統一
    job_id: deploymentData.finetuning_job_id, // ✅ number型
    status: deploymentData.status as "active" | "inactive",
    endpoint: deploymentData.endpoint ?? "", // ✅ null安全
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
        <DeploymentMethodsCard methods={methods} />
      </div>

      <DeploymentTestCard deploymentId={String(deployment.id)} />
      <DeploymentDangerZone
        deploymentId={String(deployment.id)}
        onDelete={handleDeleteDeployment}
      />
    </div>
  );
}
