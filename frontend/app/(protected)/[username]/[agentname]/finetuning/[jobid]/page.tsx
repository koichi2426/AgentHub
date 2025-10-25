"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { notFound } from "next/navigation";
import Cookies from "js-cookie";

import { getUserAgents, AgentListItem } from "@/fetchs/get_user_agents/get_user_agents";
import {
  getUserFinetuningJobs,
  FinetuningJobListItem,
} from "@/fetchs/get_user_finetuning_jobs/get_user_finetuning_jobs";

import type { Agent, FinetuningJob, Visualizations } from "@/lib/data";

import JobDetailHeader from "@/components/finetuning/JobDetailHeader";
import JobSummaryCard from "@/components/finetuning/JobSummaryCard";
import TrainingDataCard from "@/components/finetuning/TrainingDataCard";
import WeightVisualizationAccordion from "@/components/finetuning/WeightVisualizationAccordion";
import JobDangerZone from "@/components/finetuning/JobDangerZone";

import weightVisualizationsData from "@/lib/mocks/weight_visualizations.json";


type JobDetailPageProps = {
  params: {
    username: string;
    agentname: string;
    jobid: string;
  };
};

export default function JobDetailPage({ params }: JobDetailPageProps) {
  const router = useRouter();
  const { username, agentname, jobid } = params;

  const [agentData, setAgentData] = useState<AgentListItem | null>(null);
  const [jobData, setJobData] = useState<FinetuningJobListItem | null>(null);
  const [visualizations, setVisualizations] = useState<Visualizations | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobAndAgentData = async () => {
      const token = Cookies.get("auth_token");
      if (!token) {
        router.push("/login");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const [jobsResponse, agentsResponse] = await Promise.all([
          getUserFinetuningJobs(token),
          getUserAgents(token)
        ]);

        const foundJob = jobsResponse.jobs.find(
          (j) => String(j.id) === String(jobid)
        );

        if (!foundJob) {
            notFound();
            return;
        }

        const foundAgent = agentsResponse.agents.find(
          (a) => String(a.id) === String(foundJob.agent_id)
        );

        if (!foundAgent) {
            notFound();
            return;
        }

        if (
            foundAgent.owner.toLowerCase() !== username.toLowerCase() ||
            foundAgent.name.toLowerCase() !== agentname.toLowerCase()
        ) {
            notFound();
            return;
        }

        setJobData(foundJob);
        setAgentData(foundAgent);

        const allVisualizations = weightVisualizationsData as unknown as Visualizations[];
        const foundVisualizations = allVisualizations.find((v) => String(v.job_id) === String(jobid));
        setVisualizations(foundVisualizations);

      } catch (e: unknown) {
        console.error("Failed to fetch job/agent data:", e);
        let errorMessage = "Failed to load job details. Please try again.";
        if (e instanceof Error) {
             if (e.message !== 'NEXT_NOT_FOUND') {
                errorMessage = e.message;
             } else {
                 return;
             }
        }
        setError(errorMessage);

      } finally {
            setIsLoading(false);
      }
    };

    fetchJobAndAgentData();
  }, [username, agentname, jobid, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading job details...
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

  if (!agentData || !jobData) {
    notFound();
    return null;
  }

  const agent = agentData as unknown as Agent;
  const job = jobData as unknown as FinetuningJob;


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