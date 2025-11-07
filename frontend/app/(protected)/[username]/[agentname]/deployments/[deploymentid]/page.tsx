"use client";

import { useEffect, useState } from "react";
import { notFound, useRouter } from "next/navigation";
import Cookies from "js-cookie";

// Fetch 関連
import { getUser } from "@/fetchs/get_user/get_user";
import { getUserAgents, AgentListItem } from "@/fetchs/get_user_agents/get_user_agents";

// Agent Finetuning Jobs fetcher
import { getAgentFinetuningJobs } from "@/fetchs/get_agent_finetuning_jobs/get_agent_finetuning_jobs"; 

import { getFinetuningJobDeployment, GetFinetuningJobDeploymentResponse } from "@/fetchs/get_finetuning_job_deployment/get_finetuning_job_deployment";

// メソッド関連の型インポート (関数のみインポート)
import { getDeploymentMethods } from "@/fetchs/get_deployment_methods/get_deployment_methods"; 

// 推論テスト関連のインポート (関数のみインポート)
import { testDeploymentInference } from "@/fetchs/test_deployment_inference/test_deployment_inference"; 

// UIコンポーネント
import DeploymentBreadcrumb from "@/components/deployments/DeploymentBreadcrumb";
import DeploymentDetailCard from "@/components/deployments/DeploymentDetailCard";
import DeploymentTestCard from "@/components/deployments/DeploymentTestCard";
import DeploymentDangerZone from "@/components/deployments/DeploymentDangerZone";
import DeploymentMethodsCard from "@/components/deployments/DeploymentMethodsCard";

// ★★★ 修正: 全てのDTO/VOを lib/data.ts からインポート ★★★
import type { 
    User, 
    Agent, 
    Deployment, 
    DeploymentTestResponse, // メインのテスト結果型
    MethodListItemDTO,      // メソッドリスト型
    FinetuningJobListItem,  // Jobリスト型
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
  
  // TestResult State の型を lib/data.ts の型に変更
  const [testResult, setTestResult] = useState<DeploymentTestResponse | null>(null); 
  
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

        // ★★★ 修正箇所: foundJobの status の型不一致を解消 ★★★
        const JobStatusUnion = ['completed', 'running', 'failed', 'queued'];
        const isStatusValid = JobStatusUnion.includes(foundJob.status.toLowerCase());

        const safeJobData = {
            ...foundJob,
            status: isStatusValid ? foundJob.status as 'completed' | 'running' | 'failed' | 'queued' : 'failed',
        } as FinetuningJobListItem;
        // ★★★ 修正箇所ここまで ★★★

        if (
          foundAgent.owner.toLowerCase() !== username.toLowerCase() ||
          foundAgent.name.toLowerCase() !== agentname.toLowerCase()
        ) {
          notFound();
        }

        setAgentData(foundAgent);
        setJobData(safeJobData); // ★ キャストしたデータを使う

        // --- Step 2: デプロイメント取得 ---
        let deployment: GetFinetuningJobDeploymentResponse | null = null;
        try {
          deployment = await getFinetuningJobDeployment(Number(foundJob.id), token);
        } catch {
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
  
  // ★★★ 修正箇所: テスト実行ハンドラを定義し、型キャストでエラーを解消 ★★★
  const handleRunTest = async (testFile: File) => {
    const token = Cookies.get("auth_token");
    if (!token) return;

    setTestResult(null); 
    setIsLoading(true); 
    setError(null);

    try {
        const requestData = { testFile };
        
        // 厳密な二段階キャストで型チェックを強制 (TS2352解消)
        const rawResult = await testDeploymentInference(requestData, deploymentData.id, token);
        const result = rawResult as unknown as DeploymentTestResponse; 
        
        setTestResult(result);
    } catch (e: unknown) { // ★ 修正: 'any' を 'unknown' に修正し、ESLint Errorを解消
        console.error("Test execution failed:", e);
        const msg = e instanceof Error ? e.message : 'Unknown error occurred.';
        setError(`Test execution failed: ${msg}`);
    } finally {
        setIsLoading(false); 
    }
  };


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

      <DeploymentTestCard 
        deploymentId={String(deployment.id)} 
        onRunTest={handleRunTest}
        testResult={testResult}
        isTestLoading={isLoading} 
        errorMessage={error} // エラーメッセージを渡す
      />
      
      <DeploymentDangerZone
        deploymentId={String(deployment.id)}
        onDelete={handleDeleteDeployment}
      />
    </div>
  );
}