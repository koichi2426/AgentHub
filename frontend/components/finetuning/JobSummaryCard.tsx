"use client";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
// model_id が削除されたため、Bot アイコンは不要
import { Calendar, CheckCircle, Clock } from "lucide-react";
// ★★★ data.ts から FinetuningJob 型をインポート ★★★
import type { FinetuningJob } from "@/lib/data";

type JobSummaryCardProps = {
  // ★★★ job の型を FinetuningJob に修正 ★★★
  job: FinetuningJob;
};

export default function JobSummaryCard({ job }: JobSummaryCardProps) {
  // model_id が削除されたため、関連する変数を削除
  // const modelIdentifier = job.model_id || "N/A (Model Not Generated)";

  return (
    <Card className="md:col-span-1">
      <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
      <CardContent className="space-y-4 text-sm">
        
        {/* model_id の表示ブロックを削除 */}

        <div className="flex items-center">
          <CheckCircle className="mr-3 h-5 w-5 text-muted-foreground" />
          <Badge variant={job.status === "completed" ? "default" : "secondary"}>{job.status}</Badge>
        </div>
        <div className="flex items-center">
          <Calendar className="mr-3 h-5 w-5 text-muted-foreground" />
          {/* ★★★ 修正: createdAt -> created_at ★★★ */}
          <div><p>{new Date(job.created_at).toLocaleString("ja-JP")}</p><p className="text-xs text-muted-foreground">Created At</p></div>
        </div>
        {/* ★★★ 修正: finishedAt -> finished_at ★★★ */}
        {job.finished_at && (
          <div className="flex items-center">
            <Clock className="mr-3 h-5 w-5 text-muted-foreground" />
            {/* ★★★ 修正: finishedAt -> finished_at ★★★ */}
            <div><p>{new Date(job.finished_at).toLocaleString("ja-JP")}</p><p className="text-xs text-muted-foreground">Finished At</p></div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}