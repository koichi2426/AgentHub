"use client";

import FineTuningUploader from "@/components/fine-tuning-uploader";
import JobHistoryTable from "@/components/job-history-table";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import type { User, Agent, FinetuningJob } from "@/lib/data";

export default function AgentTabFineTuning({
  user,
  agent,
  jobs,
}: {
  user: User;
  agent: Agent;
  jobs: FinetuningJob[];
}) {
  return (
    <>
      <FineTuningUploader agentId={agent.id} />
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Job History</CardTitle>
        </CardHeader>
        <CardContent>
          <JobHistoryTable
            jobs={jobs}
            username={user.name}
            agentname={agent.name}
          />
        </CardContent>
      </Card>
    </>
  );
}
