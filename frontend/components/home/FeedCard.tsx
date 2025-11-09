"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot } from "lucide-react";

interface FeedCardProps {
  isLoading: boolean;
  agents: {
    id: number;
    owner: string;
    name: string;
    description?: string | null; // ← ✅ null も許容に修正
  }[];
}

export function FeedCard({ isLoading, agents }: FeedCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Feed</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading feed...</p>
        ) : agents.length > 0 ? (
          <ul className="space-y-4">
            {agents.map((agent) => (
              <li key={agent.id} className="border-b pb-4 last:border-b-0">
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4" />
                  <span className="text-xl font-bold text-blue-500 truncate">
                    {agent.owner}/{agent.name}
                  </span>
                </div>
                {agent.description && (
                  <p className="text-muted-foreground mt-2">{agent.description}</p>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">No agents yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
