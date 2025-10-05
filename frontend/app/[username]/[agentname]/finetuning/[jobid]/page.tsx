"use client"; // paramsを安全に扱うためClient Componentに

import { useMemo } from "react"; // useMemoをインポート
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Bot, Calendar, CheckCircle, Clock } from "lucide-react";
import Link from "next/link";
import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import jobs from "@/lib/mocks/finetuning_jobs.json";
import trainingData from "@/lib/mocks/triplet_data.json";
import { notFound } from "next/navigation";

type JobDetailPageProps = {
  params: {
    username: string;
    agentname: string;
    jobid: string;
  };
};

export default function JobDetailPage({ params }: JobDetailPageProps) {
  // ↓↓ データ検索ロジックをuseMemoでラップしました ↓↓
  const { agent, job, dataUsed } = useMemo(() => {
    const foundAgent = agents.find(
      (a) =>
        a.owner.toLowerCase() === params.username.toLowerCase() &&
        a.name.toLowerCase() === params.agentname.toLowerCase()
    );

    const foundJob = jobs.find((j) => j.id === params.jobid);

    const foundData = trainingData.find((d) => d.jobId === params.jobid);

    return { agent: foundAgent, job: foundJob, dataUsed: foundData };
  }, [params.username, params.agentname, params.jobid]);

  if (!agent || !job) {
    notFound();
  }

  return (
    <div className="container mx-auto max-w-4xl p-4 md:p-10">
      <div className="mb-8 flex flex-col gap-4">
        <Link
          href={`/${params.username}/${params.agentname}`}
          className="flex items-center text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to {agent.name}
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Fine-tuning Job Details</h1>
          <p className="font-mono text-sm text-muted-foreground">{job.id}</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex items-center">
              <Bot className="mr-3 h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-semibold">{job.modelId}</p>
                <p className="text-xs text-muted-foreground">Model ID</p>
              </div>
            </div>
            <div className="flex items-center">
              <CheckCircle className="mr-3 h-5 w-5 text-muted-foreground" />
              <Badge
                variant={job.status === "completed" ? "default" : "secondary"}
              >
                {job.status}
              </Badge>
            </div>
            <div className="flex items-center">
              <Calendar className="mr-3 h-5 w-5 text-muted-foreground" />
              <div>
                <p>{new Date(job.createdAt).toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">Created At</p>
              </div>
            </div>
            {job.finishedAt && (
              <div className="flex items-center">
                <Clock className="mr-3 h-5 w-5 text-muted-foreground" />
                <div>
                  <p>{new Date(job.finishedAt).toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">Finished At</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          {/* ↓↓ ここの閉じタグを修正しました ↓↓ */}
          <CardHeader>
            <CardTitle>Training Data Used</CardTitle>
            <CardDescription>
              A sample of the triplet data submitted for this job.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {dataUsed ? (
              <pre className="mt-2 w-full rounded-md bg-muted p-4">
                <code className="text-sm text-muted-foreground">
                  {JSON.stringify(dataUsed.data, null, 2)}
                </code>
              </pre>
            ) : (
              <p className="text-sm text-muted-foreground">
                No training data found for this job.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

