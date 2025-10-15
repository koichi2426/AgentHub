"use client";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, Calendar, CheckCircle, Clock } from "lucide-react";
// ★★★ data.ts から FinetuningJob 型をインポート ★★★
import type { FinetuningJob } from "@/lib/data";

type JobSummaryCardProps = {
  // ★★★ job の型を FinetuningJob に修正 ★★★
  job: FinetuningJob;
};

export default function JobSummaryCard({ job }: JobSummaryCardProps) {
  return (
    <Card className="md:col-span-1">
      <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
      <CardContent className="space-y-4 text-sm">
        <div className="flex items-center">
          <Bot className="mr-3 h-5 w-5 text-muted-foreground" />
          <div><p className="font-semibold">{job.modelId}</p><p className="text-xs text-muted-foreground">Model ID</p></div>
        </div>
        <div className="flex items-center">
          <CheckCircle className="mr-3 h-5 w-5 text-muted-foreground" />
          <Badge variant={job.status === "completed" ? "default" : "secondary"}>{job.status}</Badge>
        </div>
        <div className="flex items-center">
          <Calendar className="mr-3 h-5 w-5 text-muted-foreground" />
          <div><p>{new Date(job.createdAt).toLocaleString("ja-JP")}</p><p className="text-xs text-muted-foreground">Created At</p></div>
        </div>
        {/* この条件分岐(job.finishedAt && ...)により、undefined の場合は何も表示されないため安全です */}
        {job.finishedAt && (
          <div className="flex items-center">
            <Clock className="mr-3 h-5 w-5 text-muted-foreground" />
            <div><p>{new Date(job.finishedAt).toLocaleString("ja-JP")}</p><p className="text-xs text-muted-foreground">Finished At</p></div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}