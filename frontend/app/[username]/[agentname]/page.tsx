"use client"; // Stateやインタラクションを扱うためClient Componentに

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation"; // useRouterをインポート
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Bot,
  Cpu,
  Rocket,
  Settings,
  Info,
  Play,
  Terminal,
} from "lucide-react";
import Link from "next/link";
import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import jobs from "@/lib/mocks/finetuning_jobs.json";
import deployments from "@/lib/mocks/deployments.json";
import { User, Agent } from "@/lib/data";
import { notFound } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

type AgentPageProps = {
  params: {
    username: string;
    agentname: string;
  };
};

export default function AgentPage({ params }: AgentPageProps) {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const { user, agent } = useMemo(() => {
    const foundUser = users.find(
      (u) => u.name.toLowerCase() === params.username.toLowerCase()
    );
    const foundAgent = agents.find(
      (a) =>
        a.owner.toLowerCase() === params.username.toLowerCase() &&
        a.name.toLowerCase() === params.agentname.toLowerCase()
    );
    return { user: foundUser, agent: foundAgent };
  }, [params.username, params.agentname]);

  if (!user || !agent) {
    notFound();
  }

  const { agentJobs, agentDeployments } = useMemo(() => {
    if (!agent) return { agentJobs: [], agentDeployments: [] };

    const filteredJobs = jobs.filter((job) => job.agentId === agent.id);
    const modelIds = [
      `model_${agent.name.toLowerCase().replace(/-/g, "")}_v1_base`,
      ...filteredJobs.map((j) => j.modelId),
    ];
    const filteredDeployments = deployments.filter((dep) =>
      modelIds.includes(dep.modelId)
    );
    return { agentJobs: filteredJobs, agentDeployments: filteredDeployments };
  }, [agent]);

  // --- JSONLファイル送信処理 ---
  const handleStartJob = async () => {
    if (!selectedFile) {
      alert("ファイルを選択してください。");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("agentId", agent?.id ?? "");

      const res = await fetch("/api/finetuning", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("ファイル送信に失敗しました");
      }

      alert("ファインチューニングジョブが開始されました。");
      setSelectedFile(null);
    } catch (e: any) {
      alert(e.message || "エラーが発生しました。");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto max-w-6xl p-4 md:p-10">
      <div className="mb-8">
        <h1 className="text-2xl font-normal">
          <Link href={`/${user.name}`} className="text-primary hover:underline">
            {user.name}
          </Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <span className="font-semibold">{agent.name}</span>
        </h1>
        <p className="mt-2 text-muted-foreground">{agent.description}</p>
      </div>

      <Tabs defaultValue="finetuning" className="w-full">
        <TabsList>
          <TabsTrigger value="finetuning">
            <Rocket className="mr-2 h-4 w-4" />
            Fine-tuning
          </TabsTrigger>
          <TabsTrigger value="api">
            <Cpu className="mr-2 h-4 w-4" />
            Deployments
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="finetuning" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Submit New Fine-tuning Job</CardTitle>
              <CardDescription>
                Upload a JSONL file containing triplet data for fine-tuning.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid w-full gap-2">
                <Label htmlFor="triplet-file">Triplet JSONL File</Label>
                <Input
                  id="triplet-file"
                  type="file"
                  accept=".jsonl"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    setSelectedFile(file || null);
                  }}
                />
                {selectedFile && (
                  <p className="text-sm text-muted-foreground mt-1">
                    選択中: {selectedFile.name}
                  </p>
                )}
              </div>
              <Button onClick={handleStartJob} disabled={uploading}>
                <Rocket className="mr-2 h-4 w-4" />
                {uploading ? "Uploading..." : "Start Job"}
              </Button>
            </CardContent>
          </Card>

          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Job History</CardTitle>
            </CardHeader>
            <CardContent>
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
                  {agentJobs.map((job) => (
                    <TableRow
                      key={job.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() =>
                        router.push(
                          `/${user.name}/${agent.name}/finetuning/${job.id}`
                        )
                      }
                    >
                      <TableCell className="font-mono text-primary">
                        {job.id}
                      </TableCell>
                      <TableCell className="font-mono">{job.modelId}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            job.status === "completed"
                              ? "default"
                              : "secondary"
                          }
                        >
                          {job.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {new Date(job.createdAt).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="mt-6">
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
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {agentDeployments.map((dep) => (
                    <TableRow key={dep.id}>
                      <TableCell className="font-mono font-medium">
                        {dep.modelId}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            dep.status === "active" ? "outline" : "secondary"
                          }
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
                      <TableCell className="text-right">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="outline" size="sm">
                              <Play className="mr-2 h-4 w-4" /> Test
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Test API Endpoint</DialogTitle>
                              <DialogDescription className="font-mono text-xs pt-2">
                                {dep.endpoint}
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4 py-4">
                              <div className="space-y-2">
                                <Label htmlFor="prompt">Prompt</Label>
                                <Input
                                  id="prompt"
                                  placeholder="Enter your test prompt..."
                                />
                              </div>
                              <div className="space-y-2">
                                <Label>Response</Label>
                                <div className="w-full rounded-md bg-muted p-4 font-mono text-xs h-32">
                                  {/* API response will appear here */}
                                </div>
                              </div>
                            </div>
                            <DialogFooter>
                              <Button>
                                <Terminal className="mr-2 h-4 w-4" /> Send
                                Request
                              </Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="mt-6">
          <p>Settings...</p>
        </TabsContent>
      </Tabs>
    </div>
  );
}
