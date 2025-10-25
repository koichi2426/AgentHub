"use client";

import { useRouter } from "next/navigation";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { FinetuningJob } from "@/lib/data"; // ★ 修正: FinetuningJob 型をインポート ★

// ★ 修正: ローカルの Job 型定義を削除 ★

export default function JobHistoryTable({
  jobs,
  username,
  agentname,
}: {
  jobs: FinetuningJob[]; // ★ 修正: FinetuningJob[] 型を使用 ★
  username: string;
  agentname: string;
}) {
  const router = useRouter();

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Job ID</TableHead>
          {/* Model ID の列を削除 */}
          <TableHead>Status</TableHead>
          <TableHead>Created At</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {jobs.map((job) => (
          <TableRow
            key={job.id}
            className="cursor-pointer hover:bg-muted/50"
            onClick={() =>
              router.push(`/${username}/${agentname}/finetuning/${job.id}`)
            }
          >
            <TableCell className="font-mono text-primary">{job.id}</TableCell>
            {/* ★ 修正: modelId -> model_id のセルを削除 ★ */}
            <TableCell>
              <Badge variant={job.status === "completed" ? "default" : "secondary"}>
                {job.status}
              </Badge>
            </TableCell>
            {/* ★ 修正: createdAt -> created_at ★ */}
            <TableCell>{new Date(job.created_at).toLocaleString()}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}