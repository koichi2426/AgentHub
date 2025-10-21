"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { notFound } from "next/navigation";

// ★★★ data.ts から必要な型をすべてインポート ★★★
import type { Agent, FinetuningJob, TrainingLink, Visualizations } from "@/lib/data";

// モックデータのインポート
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
    const foundJob = (jobs as FinetuningJob[]).find((j) => j.id === params.jobid);
    if (!foundJob) return { agent: undefined, job: undefined, trainingLink: undefined, visualizations: undefined };

    const foundAgent = (agents as Agent[]).find((a) => a.id === foundJob.agentId && a.owner.toLowerCase() === params.username.toLowerCase());
    const foundTrainingLink = (trainingDataLinks as TrainingLink[]).find((d) => d.jobId === params.jobid);
    const foundVisualizations = (weightVisualizationsData as Visualizations[]).find((v) => v.jobId === params.jobid);

    return { agent: foundAgent, job: foundJob, trainingLink: foundTrainingLink, visualizations: foundVisualizations };
  }, [params.username, params.jobid]);

  if (!agent || !job) {
    notFound();
  }

  const handleDeleteModel = () => {
    console.log(`Deleting model: ${job.modelId} associated with job: ${job.id}`);
    alert(`モデル「${job.modelId}」を削除しました。(シミュレーション)`);
    router.push(`/${params.username}/${params.agentname}`);
  };

  const handleDeployModel = () => {
    console.log(`Deploying model: ${job.modelId}`);
    alert(`モデル「${job.modelId}」のデプロイを開始しました。(シミュレーション)`);
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