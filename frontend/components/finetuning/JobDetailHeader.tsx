"use client";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

type JobDetailHeaderProps = {
  agent: { name: string };
  job: { id: number | string; status: string }; // ← number を許容
  params: { username: string; agentname: string };
};

export default function JobDetailHeader({ agent, job, params }: JobDetailHeaderProps) {
  return (
    <div className="mb-8 flex flex-col gap-4">
      <Link
        href={`/${params.username}/${params.agentname}`}
        className="flex items-center text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to {agent.name}
      </Link>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Fine-tuning Job Details</h1>
          {/* idがnumberの場合も安全に表示 */}
          <p className="font-mono text-sm text-muted-foreground">{String(job.id)}</p>
        </div>
      </div>
    </div>
  );
}
