"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { notFound } from "next/navigation";

// ★★★ data.ts から必要な型をすべてインポート ★★★
import type { Agent, FinetuningJob, Deployment, User, TrainingLink, Visualizations } from "@/lib/data"; // 必要な型を明示的にインポート

// モックデータのインポート (ビルド時にエラーの原因となる可能性が高いが、ここでは依存を維持)
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
    // ★★★ 修正1: モックデータに新しい型を適用 (unknown経由で強制) ★★★
    const allJobs = jobs as unknown as FinetuningJob[];
    const allAgents = agents as unknown as Agent[];
    const allTrainingLinks = trainingDataLinks as unknown as TrainingLink[];
    const allVisualizations = weightVisualizationsData as unknown as Visualizations[];
    
    const foundJob = allJobs.find((j) => j.id === params.jobid);
    if (!foundJob) return { agent: undefined, job: undefined, trainingLink: undefined, visualizations: undefined };

    // ★★★ 修正2: job.agentId -> job.agent_id に修正 ★★★
    // agent_id は number なので、型変換が必要かもしれませんが、ここではDBの型に従いそのまま比較
    const foundAgent = allAgents.find((a) => String(a.id) === String(foundJob.agent_id) && a.owner.toLowerCase() === params.username.toLowerCase());
    
    const foundTrainingLink = allTrainingLinks.find((d) => d.job_id === params.jobid); // ★ 修正3: jobId -> job_id ★
    const foundVisualizations = allVisualizations.find((v) => v.job_id === params.jobid); // ★ 修正4: jobId -> job_id ★

    return { agent: foundAgent, job: foundJob, trainingLink: foundTrainingLink, visualizations: foundVisualizations };
  }, [params.username, params.jobid]);

  if (!agent || !job) {
    notFound();
  }
  
  // NOTE: job.model_id は null の可能性があるため、使用前に null チェックが必要です。
  const modelId = job.model_id;

  const handleDeleteModel = () => {
    console.log(`Deleting model: ${modelId} associated with job: ${job.id}`);
    if (modelId) {
      alert(`モデル「${modelId}」を削除しました。(シミュレーション)`);
    } else {
      alert("モデルIDがありません。");
    }
    router.push(`/${params.username}/${params.agentname}`);
  };

  const handleDeployModel = () => {
    console.log(`Deploying model: ${modelId}`);
    if (modelId) {
      alert(`モデル「${modelId}」のデプロイを開始しました。(シミュレーション)`);
    } else {
      alert("モデルIDがありません。デプロイできません。");
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