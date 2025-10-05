import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bot, Cpu, Rocket, Settings, Info } from "lucide-react";
import Link from "next/link";
import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import { User } from "@/lib/data";
import { notFound } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

type AgentPageProps = {
  params: {
    username: string;
    agentname: string;
  };
};

export default function AgentPage({ params }: AgentPageProps) {
  const user = users.find(
    (u: User) => u.name.toLowerCase() === params.username.toLowerCase()
  );

  const agent = agents.find(
    (a) =>
      a.owner.toLowerCase() === params.username.toLowerCase() &&
      a.name.toLowerCase() === params.agentname.toLowerCase()
  );

  if (!user || !agent) {
    notFound();
  }

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
      <Tabs defaultValue="finetuning" className="w-full">
        <TabsList>
          <TabsTrigger value="finetuning">
            <Rocket className="mr-2 h-4 w-4" />
            Fine-tuning
          </TabsTrigger>
          <TabsTrigger value="api">
            <Cpu className="mr-2 h-4 w-4" />
            API
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
              <CardTitle>Submit Triplet Data</CardTitle>
              <CardDescription>
                Provide triplet data (anchor, positive, negative) in JSON
                format to start the fine-tuning process.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid w-full gap-2">
                <Label htmlFor="triplet-data">Triplet JSON Data</Label>
                <Textarea
                  id="triplet-data"
                  placeholder={`[
  {
    "anchor": "What is the capital of France?",
    "positive": "Paris is the capital of France.",
    "negative": "Berlin is the capital of Germany."
  }
]`}
                  rows={10}
                />
              </div>
              <Button>
                <Rocket className="mr-2 h-4 w-4" /> Start Fine-tuning Job
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API タブ */}
        <TabsContent value="api" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>API Management</CardTitle>
              <CardDescription>
                Manage the API endpoint for this agent.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>API Status: Inactive</AlertTitle>
                <AlertDescription>
                  The API is not currently running. Start the API to make this
                  agent available for requests.
                </AlertDescription>
              </Alert>
              <Button>
                <Cpu className="mr-2 h-4 w-4" /> Start API
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings タブ */}
        <TabsContent value="settings" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Agent Settings</CardTitle>
              <CardDescription>
                General settings for this agent.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>Settings content will be here...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
