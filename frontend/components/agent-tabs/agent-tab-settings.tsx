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
import type { Agent } from "@/lib/data";

export default function AgentTabSettings({ agent }: { agent: Agent }) {
  
  // メソッド設定に関するState（methods, newMethod）とuseEffectは全て削除

  const saveSettings = async () => {
    // 現在はモック動作（API接続時にPOST処理へ置換可能）
    console.log("Saving settings for agent:", agent.name);
    alert("Settings saved successfully!");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Settings</CardTitle>
        <CardDescription>
          Manage advanced settings for <strong>{agent.name}</strong>.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        
        {/* メソッド設定UIが削除されたことによる代替のプレースホルダー */}
        <div className="p-4 border rounded bg-muted/20">
          <p className="text-sm text-muted-foreground">
            No configurable settings available yet. Additional fields will be added here.
          </p>
        </div>
        
        <Button className="mt-4 w-full" onClick={saveSettings}>
          Save Settings
        </Button>
      </CardContent>
    </Card>
  );
}