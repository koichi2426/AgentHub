"use client";

import { Separator } from "@/components/ui/separator";
import { Bot } from "lucide-react";
import Link from "next/link";

interface UserAgentsListProps {
  isLoading: boolean;
  agents: { id: number; owner: string; name: string }[];
}

export function UserAgentsList({ isLoading, agents }: UserAgentsListProps) {
  return (
    <div className="w-full">
      <h2 className="font-semibold text-lg mt-4">Agents</h2>
      <Separator className="mb-2" />

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading...</p>
      ) : agents.length > 0 ? (
        agents.map((agent) => (
          <div key={agent.id} className="flex items-center gap-2 text-sm">
            <Bot className="w-4 h-4 text-muted-foreground" />
            <Link
              href={`/${agent.owner}/${agent.name}`}
              className="hover:underline truncate"
            >
              {agent.owner}/{agent.name}
            </Link>
          </div>
        ))
      ) : (
        <p className="text-sm text-muted-foreground">No agents found.</p>
      )}
    </div>
  );
}
