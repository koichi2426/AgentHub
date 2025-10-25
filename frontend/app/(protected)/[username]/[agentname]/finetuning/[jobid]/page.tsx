"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { notFound } from "next/navigation";

// Type Imports
import type { Agent, FinetuningJob, Deployment, User, Visualizations } from "@/lib/data"; 

// Mock Data Imports
import agents from "@/lib/mocks/agents.json";
import jobs from "@/lib/mocks/finetuning_jobs.json";
import weightVisualizationsData from "@/lib/mocks/weight_visualizations.json";

// Component Imports
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

  const { agent, job, visualizations } : {
    agent: Agent | undefined;
    job: FinetuningJob | undefined;
    visualizations: Visualizations | undefined;
  } = useMemo(() => {
    const allJobs = jobs as unknown as FinetuningJob[];
    const allAgents = agents as unknown as Agent[];
    const allVisualizations = weightVisualizationsData as unknown as Visualizations[];
    
    const foundJob = allJobs.find((j) => j.id === params.jobid);
    if (!foundJob) return { agent: undefined, job: undefined, visualizations: undefined };

    const foundAgent = allAgents.find((a) => String(a.id) === String(foundJob.agent_id) && a.owner.toLowerCase() === params.username.toLowerCase());
    
    const foundVisualizations = allVisualizations.find((v) => v.job_id === params.jobid); 

    return { agent: foundAgent, job: foundJob, visualizations: foundVisualizations };
  }, [params.username, params.jobid]);

  if (!agent || !job) {
    notFound();
  }
  
  const handleDeleteModel = () => {
    console.log(`Deleting job: ${job.id}`);
    alert(`ジョブ「${job.id}」を削除します。(シミュレーション)`);
    router.push(`/${params.username}/${params.agentname}`);
  };

  const handleDeployModel = () => {
    console.log(`Deploying results of job: ${job.id}`);
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
        <TrainingDataCard job={job} /> 
      </div>

      {visualizations && (
        <WeightVisualizationAccordion visualizations={visualizations} />
      )}

      <JobDangerZone job={job} onDelete={handleDeleteModel} />
    </div>
  );
}