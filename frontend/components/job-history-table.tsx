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

type Job = {
  id: string;
  modelId: string;
  status: string;
  createdAt: string;
};

export default function JobHistoryTable({
  jobs,
  username,
  agentname,
}: {
  jobs: Job[];
  username: string;
  agentname: string;
}) {
  const router = useRouter();

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Job ID</TableHead>
          <TableHead>Model ID</TableHead>
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
            <TableCell className="font-mono">{job.modelId}</TableCell>
            <TableCell>
              <Badge variant={job.status === "completed" ? "default" : "secondary"}>
                {job.status}
              </Badge>
            </TableCell>
            <TableCell>{new Date(job.createdAt).toLocaleString()}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
