"use client";

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
import { Switch } from "@/components/ui/switch";
import type { Deployment } from "@/lib/data";

export default function AgentTabDeployments({
  deployments,
}: {
  deployments: Deployment[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Model Deployments</CardTitle>
        <CardDescription>
          Manage and test API endpoints for your fine-tuned models.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Model ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Endpoint</TableHead>
              <TableHead className="text-center">Activate</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {deployments.map((dep) => (
              <TableRow key={dep.id}>
                <TableCell className="font-mono font-medium">
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
                <TableCell className="text-center">
                  <Switch checked={dep.status === "active"} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
