"use client";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, CheckCircle, Clock } from "lucide-react";
import type { FinetuningJob } from "@/lib/data";

type JobSummaryCardProps = {
  job: FinetuningJob;
};

export default function JobSummaryCard({ job }: JobSummaryCardProps) {
  return (
    <Card className="md:col-span-1">
      <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
      <CardContent className="space-y-4 text-sm">
        
        <div className="flex items-center">
          <CheckCircle className="mr-3 h-5 w-5 text-muted-foreground" />
          <Badge variant={job.status === "completed" ? "default" : "secondary"}>{job.status}</Badge>
        </div>
        <div className="flex items-center">
          <Calendar className="mr-3 h-5 w-5 text-muted-foreground" />
          <div><p>{new Date(job.created_at).toLocaleString("ja-JP")}</p><p className="text-xs text-muted-foreground">Created At</p></div>
        </div>
        {job.finished_at && (
          <div className="flex items-center">
            <Clock className="mr-3 h-5 w-5 text-muted-foreground" />
            <div><p>{new Date(job.finished_at).toLocaleString("ja-JP")}</p><p className="text-xs text-muted-foreground">Finished At</p></div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}