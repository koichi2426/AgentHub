// frontend/app/(protected)/[username]/[agentname]/finetuning/[jobid]/page.tsx

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
import { 
  getWeightVisualizations, 
  GetWeightVisualizationsResponse, 
} from "@/fetchs/get_weight_visualizations/get_weight_visualizations";
import { API_URL } from "@/fetchs/config"; 

import type { Agent, FinetuningJob, Visualizations } from "@/lib/data";

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

const VISUALS_BASE_URL = `${API_URL}/v1/visuals/`;


export default function JobDetailPage({ params }: JobDetailPageProps) {
  const router = useRouter();
  const { username, agentname, jobid } = params;

  const [agentData, setAgentData] = useState<AgentListItem | null>(null);
  const [jobData, setJobData] = useState<FinetuningJobListItem | null>(null);
  const [visualizations, setVisualizations] = useState<GetWeightVisualizationsResponse | undefined>(undefined);
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

        let foundVisualizations: GetWeightVisualizationsResponse | undefined = undefined;
        
        if (foundJob.status === "completed") {
            try {
                const rawVisualizations = await getWeightVisualizations(token, jobid);
                
                const transformedVisualizations: GetWeightVisualizationsResponse = {
                    ...rawVisualizations,
                    layers: rawVisualizations.layers.map(layer => ({
                        ...layer,
                        weights: layer.weights.map(weight => ({
                            ...weight,
                            before_url: `${VISUALS_BASE_URL}${weight.before_url}`,
                            after_url: `${VISUALS_BASE_URL}${weight.after_url}`,
                            delta_url: `${VISUALS_BASE_URL}${weight.delta_url}`,
                        }))
                    }))
                };

                foundVisualizations = transformedVisualizations;

            } catch (visError) {
                console.warn(`WARN: Could not fetch visualizations for job ${jobid}.`, visError);
            }
        }
        
        setJobData(foundJob);
        setAgentData(foundAgent);
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
  const visualizationsCasted = visualizations as unknown as Visualizations | undefined;


  const handleDeleteModel = () => {
    console.log(`Deleting job: ${job.id}`);
    alert(`ジョブ「${job.id}」を削除します。(シミュレーション)`);
    router.push(`/${params.username}/${params.agentname}`);
  };

  return (
    <div className="container mx-auto max-w-4xl p-4 md:p-10">
      <JobDetailHeader agent={agent} job={job} params={params} /> 

      <div className="grid gap-6 md:grid-cols-3">
        <JobSummaryCard job={job} />
        <TrainingDataCard job={job} />
      </div>

      {visualizationsCasted && (
        <WeightVisualizationAccordion visualizations={visualizationsCasted} />
      )}

      <JobDangerZone job={job} onDelete={handleDeleteModel} />
    </div>
  );
}