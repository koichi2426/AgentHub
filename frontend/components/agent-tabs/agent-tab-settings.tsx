"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Trash2 } from "lucide-react";
import methodsData from "@/lib/mocks/methods.json";
import type { Agent } from "@/lib/data";

type MethodsEntry = {
  agentId: string;
  methods: string[];
};

export default function AgentTabSettings({ agent }: { agent: Agent }) {
  const [methods, setMethods] = useState<string[]>([]);
  const [newMethod, setNewMethod] = useState("");

  // --- 初回ロード時にモックデータから対象エージェントのメソッドを抽出 ---
  useEffect(() => {
    const entry = (methodsData as MethodsEntry[]).find(
      (m) => m.agentId === agent.id
    );
    if (entry) setMethods(entry.methods);
  }, [agent.id]);

  const addMethod = () => {
    if (newMethod.trim() && !methods.includes(newMethod.trim())) {
      setMethods([...methods, newMethod.trim()]);
      setNewMethod("");
    }
  };

  const removeMethod = (method: string) => {
    setMethods(methods.filter((m) => m !== method));
  };

  const saveSettings = async () => {
    // 現在はモック動作（API接続時にPOST処理へ置換可能）
    console.log("Saving methods for agent:", agent.id, methods);
    alert("Methods saved successfully!");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Settings</CardTitle>
        <CardDescription>
          Manage the callable methods for <strong>{agent.name}</strong>.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="font-semibold mb-2">Selectable Methods</h3>
          <div className="space-y-2">
            {methods.length === 0 && (
              <p className="text-sm text-muted-foreground">
                No methods registered yet.
              </p>
            )}
            {methods.map((method) => (
              <div
                key={method}
                className="flex items-center justify-between p-2 border rounded"
              >
                <span className="font-mono text-sm">{method}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeMethod(method)}
                >
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-2 mt-4">
          <Input
            placeholder="add new method..."
            value={newMethod}
            onChange={(e) => setNewMethod(e.target.value)}
          />
          <Button onClick={addMethod}>
            <Plus className="h-4 w-4 mr-1" /> Add
          </Button>
        </div>

        <Button className="mt-4 w-full" onClick={saveSettings}>
          Save Settings
        </Button>
      </CardContent>
    </Card>
  );
}
