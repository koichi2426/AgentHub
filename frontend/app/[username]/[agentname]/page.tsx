"use client"; // Stateやインタラクションを扱うためClient Componentに

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
import { User, Agent, FinetuningJob, Deployment } from "@/lib/data";
import { notFound } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
  // ↓↓ ここから下の4つの変数定義の型指定を削除しました ↓↓
  const user = users.find(
    (u) => u.name.toLowerCase() === params.username.toLowerCase()
  );
  const agent = agents.find(
    (a) =>
      a.owner.toLowerCase() === params.username.toLowerCase() &&
      a.name.toLowerCase() === params.agentname.toLowerCase()
  );

  if (!user || !agent) {
    notFound();
  }

  const agentJobs = jobs.filter(
    (job) => job.agentId === agent.id
  );
  // ベースモデルとファインチューニングで生成されたモデルのIDリストを作成
  const agentModelIds = [
    `model_${agent.name.toLowerCase().replace(/-/g, "")}_v1_base`, // 仮のベースモデルID
    ...agentJobs.map((j) => j.modelId),
  ];
  const agentDeployments = deployments.filter((dep) =>
    agentModelIds.includes(dep.modelId)
  );
  // ↑↑ ここまで ↑↑

  return (
    <div className="container mx-auto max-w-6xl p-4 md:p-10">
      {/* ヘッダー部分 */}
      <div className="mb-8">
        <h1 className="text-2xl font-normal">
          <Link
            href={`/${user.name}`}
            className="text-primary hover:underline"
          >
            {user.name}
          </Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <span className="font-semibold">{agent.name}</span>
        </h1>
        <p className="mt-2 text-muted-foreground">{agent.description}</p>
      </div>

      {/* タブコンテンツ */}
      <Tabs defaultValue="api" className="w-full">
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

        {/* Fine-tuning タブ */}
        <TabsContent value="finetuning" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Submit New Fine-tuning Job</CardTitle>
              <CardDescription>
                Provide triplet data to create a new version of your agent
                model.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid w-full gap-2">
                <Label htmlFor="triplet-data">Triplet JSON Data</Label>
                <Textarea id="triplet-data" placeholder={`[ ... ]`} rows={8} />
              </div>
              <Button>
                <Rocket className="mr-2 h-4 w-4" /> Start Job
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
                    <TableRow key={job.id}>
                      <TableCell className="font-mono">{job.id}</TableCell>
                      <TableCell className="font-mono">
                        {job.modelId}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            job.status === "completed" ? "default" : "secondary"
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

        {/* Deployments(API) タブ */}
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

        {/* Settings タブ */}
        <TabsContent value="settings" className="mt-6">
          <p>Settings...</p>
        </TabsContent>
      </Tabs>
    </div>
  );
}

