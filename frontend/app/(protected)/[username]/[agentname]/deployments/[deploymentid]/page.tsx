"use client";

import { useEffect, useState } from "react";
import { notFound, useRouter } from "next/navigation";
import Cookies from "js-cookie";

// Fetch 関連
import { getUser } from "@/fetchs/get_user/get_user";
import { getUserAgents, AgentListItem } from "@/fetchs/get_user_agents/get_user_agents";
import { getAgentFinetuningJobs } from "@/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs";
import { getFinetuningJobDeployment, GetFinetuningJobDeploymentResponse } from "@/fetchs/get_finetuning_job_deployment/get_finetuning_job_deployment";
import { getDeploymentMethods } from "@/fetchs/get_deployment_methods/get_deployment_methods";
import { testDeploymentInference } from "@/fetchs/test_deployment_inference/test_deployment_inference";

// UI コンポーネント
import DeploymentBreadcrumb from "@/components/deployments/DeploymentBreadcrumb";
import DeploymentDetailCard from "@/components/deployments/DeploymentDetailCard";
import DeploymentTestCard from "@/components/deployments/DeploymentTestCard";
import DeploymentDangerZone from "@/components/deployments/DeploymentDangerZone";
import DeploymentMethodsCard from "@/components/deployments/DeploymentMethodsCard";

// 型
import type {
  User,
  Agent,
  Deployment,
  DeploymentTestResponse,
  MethodListItemDTO,
  FinetuningJobListItem,
} from "@/lib/data";

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
  const [testResult, setTestResult] = useState<DeploymentTestResponse | null>(null);

  // 👇 ページロードとテスト実行のローディングを分離
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [isTestLoading, setIsTestLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ---------------------------------------
  // 初期ロード処理
  // ---------------------------------------
  useEffect(() => {
    const fetchDeploymentData = async () => {
      const token = Cookies.get("auth_token");
      if (!token) {
        router.push("/login");
        return;
      }

      setIsPageLoading(true);
      setError(null);

      try {
        // --- Step 0: 認証ユーザー ---
        const currentUser = await getUser(token);
        if (currentUser.username.toLowerCase() !== username.toLowerCase()) {
          notFound();
          return;
        }
        setUser(currentUser);

        // --- Step 1: Agent & Job 確認 ---
        const agentsRes = await getUserAgents(token);
        const foundAgent = agentsRes.agents.find(
          (a) =>
            a.owner.toLowerCase() === username.toLowerCase() &&
            a.name.toLowerCase() === agentname.toLowerCase()
        );
        if (!foundAgent) notFound();

        const jobsRes = await getAgentFinetuningJobs(foundAgent.id, token);
        const foundJob = jobsRes.jobs.find(
          (j) => Number(j.id) === Number(deploymentid)
        );
        if (!foundJob) notFound();

        const JobStatusUnion = ["completed", "running", "failed", "queued"];
        const isStatusValid = JobStatusUnion.includes(foundJob.status.toLowerCase());
        const safeJobData = {
          ...foundJob,
          status: isStatusValid
            ? (foundJob.status as "completed" | "running" | "failed" | "queued")
            : "failed",
        } as FinetuningJobListItem;

        setAgentData(foundAgent);
        setJobData(safeJobData);

        // --- Step 2: デプロイメント取得 ---
        const deployment = await getFinetuningJobDeployment(Number(foundJob.id), token);
        setDeploymentData(deployment);

        // --- Step 3: メソッド一覧 ---
        try {
          const methodsRes = await getDeploymentMethods(Number(foundJob.id), token);
          setMethods(methodsRes.methods);
        } catch {
          console.warn("WARN: getDeploymentMethods failed, assuming empty list.");
          setMethods([]);
        }
      } catch (e: unknown) {
        console.error("Failed to fetch deployment data:", e);
        const msg =
          e instanceof Error && e.message !== "NEXT_NOT_FOUND"
            ? e.message
            : "Failed to load deployment details.";
        setError(msg);
      } finally {
        setIsPageLoading(false);
      }
    };

    fetchDeploymentData();
  }, [username, agentname, deploymentid, router]);

  // ---------------------------------------
  // テスト実行ハンドラ
  // ---------------------------------------
  const handleRunTest = async (testFile: File) => {
    const token = Cookies.get("auth_token");
    if (!token) return;

    setTestResult(null);
    setIsTestLoading(true);
    setError(null);

    try {
      const requestData = { testFile };
      const rawResult = await testDeploymentInference(requestData, deploymentData!.id, token);
      const result = rawResult as unknown as DeploymentTestResponse;
      setTestResult(result);
    } catch (e: unknown) {
      console.error("Test execution failed:", e);
      const msg = e instanceof Error ? e.message : "Unknown error occurred.";
      setError(`Test execution failed: ${msg}`);
    } finally {
      setIsTestLoading(false);
    }
  };

  // ---------------------------------------
  // レンダリング
  // ---------------------------------------
  if (isPageLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading deployment details...
      </div>
    );
  }

  if (error && !deploymentData) {
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

  const methodNames: string[] = methods.map((m) => m.name);

  const handleDeleteDeployment = () => {
    console.log(`Deleting deployment: ${deployment.id}`);
    alert(`デプロイメント「${deployment.id}」を削除しました。(シミュレーション)`);
    router.push(`/${username}/${agentname}`);
  };

  // ---------------------------------------
  // UI
  // ---------------------------------------
  return (
    <div className="container mx-auto max-w-4xl p-6">
      <DeploymentBreadcrumb user={user} agent={agent} deploymentId={String(deployment.id)} />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DeploymentDetailCard deployment={deployment} />
        </div>
        <DeploymentMethodsCard methods={methodNames} />
      </div>

      <DeploymentTestCard
        deploymentId={String(deployment.id)}
        onRunTest={handleRunTest}
        testResult={testResult}
        isTestLoading={isTestLoading} // 👈 ここを修正
        errorMessage={error}
      />

      <DeploymentDangerZone
        deploymentId={String(deployment.id)}
        onDelete={handleDeleteDeployment}
      />
    </div>
  );
}
