"use client";
import Link from "next/link";
import type { User, Agent } from "@/lib/data";

type DeploymentBreadcrumbProps = {
  user: User;
  agent: Agent;
  deploymentId: string;
};

export default function DeploymentBreadcrumb({ user, agent, deploymentId }: DeploymentBreadcrumbProps) {
  return (
    <div className="mb-6">
      <h1 className="text-2xl font-normal">
        <Link href={`/${user.name}`} className="text-primary hover:underline">{user.name}</Link>
        <span className="mx-2 text-muted-foreground">/</span>
        <Link href={`/${user.name}/${agent.name}`} className="text-primary hover:underline">{agent.name}</Link>
        <span className="mx-2 text-muted-foreground">/</span>
        <span className="font-semibold">{deploymentId}</span>
      </h1>
    </div>
  );
}