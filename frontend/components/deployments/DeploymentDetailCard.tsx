"use client";
import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Power } from "lucide-react";
import type { Deployment } from "@/lib/data";

type DeploymentDetailCardProps = {
  deployment: Deployment;
};

export default function DeploymentDetailCard({ deployment }: DeploymentDetailCardProps) {
  const [apiStatus, setApiStatus] = useState<"active" | "inactive">(deployment.status);

  const toggleApiStatus = async () => {
    const nextStatus = apiStatus === "active" ? "inactive" : "active";
    setApiStatus(nextStatus);
    await new Promise((resolve) => setTimeout(resolve, 500));
    alert(`API を${nextStatus === "active" ? "起動" : "停止"}しました（モック）`);
  };

  return (
    <Card>
      <CardHeader><CardTitle>Deployment Details</CardTitle></CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-y-2">
          <div className="text-sm text-muted-foreground">Model ID</div>
          <div className="font-mono">{deployment.modelId}</div>
          <div className="text-sm text-muted-foreground">Status</div>
          <div>
            <Badge variant={apiStatus === "active" ? "outline" : "secondary"}>
              <span className={`mr-2 h-2 w-2 rounded-full ${apiStatus === "active" ? "bg-green-500" : "bg-gray-500"}`}></span>
              {apiStatus}
            </Badge>
          </div>
          <div className="text-sm text-muted-foreground">Endpoint</div>
          <div className="font-mono text-xs break-all">{deployment.endpoint}</div>
          <div className="text-sm text-muted-foreground">Created At</div>
          <div>{new Date(deployment.createdAt).toLocaleString("ja-JP")}</div>
        </div>
        <div className="pt-2">
          <Button variant={apiStatus === "active" ? "destructive" : "default"} onClick={toggleApiStatus}>
            <Power className="mr-2 h-4 w-4" />
            {apiStatus === "active" ? "Stop API" : "Start API"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}