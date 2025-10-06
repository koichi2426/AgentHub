"use client";

import { useRouter } from "next/navigation";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Deployment } from "@/lib/data";

export default function AgentTabDeployments({
  deployments,
  username,
  agentname,
}: {
  deployments: Deployment[];
  username: string;
  agentname: string;
}) {
  const router = useRouter();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Model Deployments</CardTitle>
        <CardDescription>
          View and access API endpoints for your fine-tuned models.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Model ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Endpoint</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {deployments.map((dep) => (
              <TableRow
                key={dep.id}
                className="cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() =>
                  router.push(`/${username}/${agentname}/deployments/${dep.id}`)
                }
              >
                <TableCell className="font-mono font-medium text-primary">
                  {dep.modelId}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={dep.status === "active" ? "outline" : "secondary"}
                  >
                    <span
                      className={`mr-2 h-2 w-2 rounded-full ${
                        dep.status === "active"
                          ? "bg-green-500"
                          : "bg-gray-500"
                      }`}
                    ></span>
                    {dep.status}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono text-xs">
                  {dep.endpoint}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
