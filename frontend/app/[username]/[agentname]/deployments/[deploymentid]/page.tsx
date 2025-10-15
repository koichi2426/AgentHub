"use client";

import { useState } from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Upload, Power, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";

import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import rawDeployments from "@/lib/mocks/deployments.json";

import type { Deployment, User, Agent } from "@/lib/data";

export default function DeploymentDetailPage({
  params,
}: {
  params: {
    username: string;
    agentname: string;
    deploymentid: string;
  };
}) {
  const { username, agentname, deploymentid } = params;
  const router = useRouter();

  const lowerUsername = username.toLowerCase();
  const lowerAgentname = agentname.toLowerCase();

  // --- ユーザーとエージェントの検索 ---
  const user: User | undefined = (users as User[]).find(
    (u) => u.name.toLowerCase() === lowerUsername
  );

  const agent: Agent | undefined = (agents as Agent[]).find(
    (a) =>
      a.owner.toLowerCase() === lowerUsername &&
      a.name.toLowerCase() === lowerAgentname
  );

  if (!user || !agent) notFound();

  // --- デプロイメントデータを型安全に変換 ---
  const deployments: Deployment[] = (rawDeployments as unknown as Deployment[]).map((dep) => ({
    ...dep,
    status:
      dep.status === "active" || dep.status === "inactive"
        ? dep.status
        : "inactive",
  }));

  const deployment = deployments.find((d) => d.id === deploymentid);
  if (!deployment) notFound();

  // --- 状態管理 ---
  const [apiStatus, setApiStatus] = useState<"active" | "inactive">(
    deployment.status
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  // --- API 起動・停止切り替え ---
  const toggleApiStatus = async () => {
    const nextStatus = apiStatus === "active" ? "inactive" : "active";
    setApiStatus(nextStatus);
    await new Promise((resolve) => setTimeout(resolve, 500));
    alert(
      `API を${nextStatus === "active" ? "起動" : "停止"}しました（モック）`
    );
  };

  // --- テスト送信関数 ---
  const handleTest = async () => {
    if (!selectedFile) {
      // ★★★ アラートメッセージを修正 ★★★
      alert("TXTファイルを選択してください。");
      return;
    }
    setTesting(true);
    setTestResult(null);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("deploymentId", deployment.id);
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setTestResult("✅ テスト送信が完了しました（モック実行）");
      setSelectedFile(null);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setTestResult(`❌ Error: ${err.message}`);
      } else {
        setTestResult("❌ Unknown error occurred.");
      }
    } finally {
      setTesting(false);
    }
  };

  // --- デプロイメント削除処理のハンドラ ---
  const handleDeleteDeployment = () => {
    console.log(`Deleting deployment: ${deployment.id}`);
    alert(`デプロイメント「${deployment.id}」を削除しました。(シミュレーション)`);
    router.push(`/${username}/${agentname}`);
  };

  // --- UI ---
  return (
    <div className="container mx-auto max-w-4xl p-6">
      {/* パンくず */}
      <div className="mb-6">
        <h1 className="text-2xl font-normal">
          <Link href={`/${user.name}`} className="text-primary hover:underline">
            {user.name}
          </Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <Link
            href={`/${user.name}/${agent.name}`}
            className="text-primary hover:underline"
          >
            {agent.name}
          </Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <span className="font-semibold">{deployment.id}</span>
        </h1>
      </div>

      {/* 詳細カード */}
      <Card>
        <CardHeader>
          <CardTitle>Deployment Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 基本情報 */}
          <div className="grid grid-cols-2 gap-y-2">
            <div className="text-sm text-muted-foreground">Model ID</div>
            <div className="font-mono">{deployment.modelId}</div>
            <div className="text-sm text-muted-foreground">Status</div>
            <div>
              <Badge variant={apiStatus === "active" ? "outline" : "secondary"}>
                <span className={`mr-2 h-2 w-2 rounded-full ${apiStatus === "active" ? "bg-green-500" : "bg-gray-500"}`}></span>
                {apiStatus}
              </Badge>
            </div>
            <div className="text-sm text-muted-foreground">Endpoint</div>
            <div className="font-mono text-xs break-all">{deployment.endpoint}</div>
            <div className="text-sm text-muted-foreground">Created At</div>
            <div>{new Date(deployment.createdAt).toLocaleString()}</div>
          </div>

          {/* API起動/停止切り替えボタン */}
          <div className="pt-2">
            <Button variant={apiStatus === "active" ? "destructive" : "default"} onClick={toggleApiStatus}>
              <Power className="mr-2 h-4 w-4" />
              {apiStatus === "active" ? "Stop API" : "Start API"}
            </Button>
          </div>

          {/* ★★★ ここからテストセクションのテキストとInput属性を修正 ★★★ */}
          <div className="pt-6 border-t mt-4">
            <h3 className="font-semibold mb-2">Test with Text Data</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Upload a Text file containing test data to simulate inference.
            </p>

            <div className="grid gap-3">
              <Label htmlFor="test-txt">Test File (.txt)</Label>
              <Input
                id="test-txt"
                type="file"
                accept=".txt"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
              {selectedFile && <p className="text-xs text-muted-foreground mt-1">選択中: {selectedFile.name}</p>}
              <Button onClick={handleTest} disabled={testing}>
                <Upload className="mr-2 h-4 w-4" />
                {testing ? "Testing..." : "Start Test"}
              </Button>
              {testResult && <div className="text-sm text-muted-foreground mt-3 border-t pt-2">{testResult}</div>}
            </div>
          </div>
          {/* ★★★ 修正ここまで ★★★ */}

        </CardContent>
      </Card>

      {/* Danger Zone */}
      <div className="mt-6">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Danger Zone</CardTitle>
            <CardDescription>
              この操作は元に戻すことができません。注意して実行してください。
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete This Deployment
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>本当に削除しますか？</AlertDialogTitle>
                  <AlertDialogDescription>
                    デプロイメント <span className="font-mono font-semibold">{deployment.id}</span> を完全に削除します。この操作は取り消せません。
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>キャンセル</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDeleteDeployment}>
                    削除を実行
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </CardContent>
        </Card>
      </div>
      
    </div>
  );
}