"use client";

import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Tag } from "lucide-react";
import { List } from "lucide-react";


export default function DeploymentMethodsCard({ methods }: { methods: string[] }) {
  return (
    <Card className="lg:col-span-1">
      <CardHeader>
        <CardTitle>Inferred Methods</CardTitle>
        <CardDescription>
          This model infers the following callable methods:
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {methods.length === 0 ? (
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <List className="h-4 w-4" />
            <p>No methods detected for this deployment.</p>
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {methods.map((method) => (
              <div
                key={method}
                className="flex items-center space-x-1 rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800 dark:bg-blue-950 dark:text-blue-200"
              >
                <Tag className="h-3 w-3" />
                <span>{method}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}