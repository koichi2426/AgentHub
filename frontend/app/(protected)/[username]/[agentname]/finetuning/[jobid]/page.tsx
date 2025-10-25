"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { notFound } from "next/navigation";

// ★★★ data.ts から必要な型をすべてインポート ★★★
import type { Agent, FinetuningJob, Deployment, User, TrainingLink, Visualizations } from "@/lib/data"; 

// モックデータのインポート (ビルドを通すために unknown as Type[] を使用)
import agents from "@/lib/mocks/agents.json";
import jobs from "@/lib/mocks/finetuning_jobs.json";
import trainingDataLinks from "@/lib/mocks/training_data_links.json"; 
import weightVisualizationsData from "@/lib/mocks/weight_visualizations.json";

// 分割したコンポーネントのインポート
import JobDetailHeader from "@/components/finetuning/JobDetailHeader";
import JobSummaryCard from "@/components/finetuning/JobSummaryCard";
import TrainingDataCard from "@/components/finetuning/TrainingDataCard";
import WeightVisualizationAccordion from "@/components/finetuning/WeightVisualizationAccordion";
import JobDangerZone from "@/components/finetuning/JobDangerZone";

type JobDetailPageProps = {
  params: {
    username: string;
    agentname: string;
    jobid: string;
  };
};

export default function JobDetailPage({ params }: JobDetailPageProps) {
  const router = useRouter();

  // 型注釈が data.ts の型を参照するようになった
  const { agent, job, trainingLink, visualizations } : {
    agent: Agent | undefined;
    job: FinetuningJob | undefined;
    trainingLink: TrainingLink | undefined;
    visualizations: Visualizations | undefined;
  } = useMemo(() => {
    // データが古い構造でもコンパイルエラーを避けるために unknown 経由でキャスト
    const allJobs = jobs as unknown as FinetuningJob[];
    const allAgents = agents as unknown as Agent[];
    const allTrainingLinks = trainingDataLinks as unknown as TrainingLink[];
    const allVisualizations = weightVisualizationsData as unknown as Visualizations[];
    
    const foundJob = allJobs.find((j) => j.id === params.jobid);
    if (!foundJob) return { agent: undefined, job: undefined, trainingLink: undefined, visualizations: undefined };

    // ★★★ 修正: AgentのIDとJobのagent_idを比較する際に、安全のため両方Stringにキャスト ★★★
    const foundAgent = allAgents.find((a) => String(a.id) === String(foundJob.agent_id) && a.owner.toLowerCase() === params.username.toLowerCase());
    
    // ★★★ 修正: スネークケースのプロパティ名を使用 ★★★
    const foundTrainingLink = allTrainingLinks.find((d) => d.job_id === params.jobid); 
    const foundVisualizations = allVisualizations.find((v) => v.job_id === params.jobid); 

    return { agent: foundAgent, job: foundJob, trainingLink: foundTrainingLink, visualizations: foundVisualizations };
  }, [params.username, params.jobid]);

  if (!agent || !job) {
    notFound();
  }
  
  // NOTE: job.model_id は削除されたため、ローカル変数も削除
  // const modelId = job.model_id;

  const handleDeleteModel = () => {
    // model_id が削除されたため、常にジョブ自体を削除するロジックのみ残す
    console.log(`Deleting job: ${job.id}`);
    alert(`ジョブ「${job.id}」を削除します。(シミュレーション)`);
    router.push(`/${params.username}/${params.agentname}`);
  };

  const handleDeployModel = () => {
    // model_id が削除されたため、ジョブIDに基づいてデプロイするロジックに変更
    console.log(`Deploying results of job: ${job.id}`);
    
    // ジョブのステータスに基づいてデプロイ可能かチェック（例）
    if (job.status === "completed") {
      alert(`ジョブ「${job.id}」の結果をデプロイします。(シミュレーション)`);
    } else {
      alert(`ジョブ「${job.id}」はまだ完了していないため、デプロイできません。`);
    }
  };

  return (
    <div className="container mx-auto max-w-4xl p-4 md:p-10">
      <JobDetailHeader agent={agent} job={job} params={params} onDeploy={handleDeployModel} />

      <div className="grid gap-6 md:grid-cols-3">
        <JobSummaryCard job={job} />
        <TrainingDataCard trainingLink={trainingLink} />
      </div>

      {visualizations && (
        <WeightVisualizationAccordion visualizations={visualizations} />
      )}

      <JobDangerZone job={job} onDelete={handleDeleteModel} />
    </div>
  );
}