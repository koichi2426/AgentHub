import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Bot } from "lucide-react";
import users from "@/lib/mocks/users.json";
import { User } from "@/lib/data";
// ↓↓ ここにAvatar関連のコンポーネントを追加しました ↓↓
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function NewAgentPage() {
  // モックデータから現在のユーザーを取得（ここでは最初のユーザーを仮定）
  const currentUser: User = users[0];

  return (
    <div className="container mx-auto max-w-3xl p-4 md:p-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Create a new Agent</h1>
        <p className="text-muted-foreground">
          An agent contains all the prompts, instructions, and configurations.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Avatar className="mr-2 h-5 w-5">
              <AvatarImage src={currentUser.avatar_url} />
              <AvatarFallback>
                {currentUser.name.substring(0, 1)}
              </AvatarFallback>
            </Avatar>
            {currentUser.name}
            <span className="mx-2">/</span>
            <span className="font-normal text-muted-foreground">Agent name</span>
          </CardTitle>
          <CardDescription>
            Choose a name and provide a description for your new agent.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="agent-name">Agent name</Label>
              <Input
                id="agent-name"
                placeholder="My-Awesome-Agent"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                placeholder="A short description of what this agent does."
              />
            </div>
          </form>
        </CardContent>
        <CardFooter>
          <Button>
            <Bot className="mr-2 h-4 w-4" /> Create Agent
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

