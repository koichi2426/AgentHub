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
import { Upload, Power, Trash2, Download } from "lucide-react";
import { useRouter } from "next/navigation";

import users from "@/lib/mocks/users.json";
import agents from "@/lib/mocks/agents.json";
import rawDeployments from "@/lib/mocks/deployments.json";

import type { Deployment, User, Agent } from "@/lib/data";

// ★★★ ここから追加 ★★★
// レポートデータの型を明確に定義
type TestReportEntry = {
  input: string;
  prediction: string;
  confidence: number;
  latency_ms: number;
};
// ★★★ ここまで追加 ★★★

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

  const user: User | undefined = (users as User[]).find(
    (u) => u.name.toLowerCase() === lowerUsername
  );
  const agent: Agent | undefined = (agents as Agent[]).find(
    (a) =>
      a.owner.toLowerCase() === lowerUsername &&
      a.name.toLowerCase() === lowerAgentname
  );
  if (!user || !agent) notFound();

  const deployment = (rawDeployments as unknown as Deployment[]).find((d) => d.id === deploymentid);
  if (!deployment) notFound();

  const [apiStatus, setApiStatus] = useState<"active" | "inactive">(deployment.status);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);
  
  // ★★★ any[] を TestReportEntry[] に修正 ★★★
  const [reportData, setReportData] = useState<TestReportEntry[] | null>(null);

  const toggleApiStatus = async () => {
    const nextStatus = apiStatus === "active" ? "inactive" : "active";
    setApiStatus(nextStatus);
    await new Promise((resolve) => setTimeout(resolve, 500));
    alert(`API を${nextStatus === "active" ? "起動" : "停止"}しました（モック）`);
  };

  const handleTest = async () => {
    if (!selectedFile) {
      alert("TXTファイルを選択してください。");
      return;
    }
    setTesting(true);
    setTestResult(null);
    setReportData(null);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      const mockReport: TestReportEntry[] = [
        { input: "User is a female tourist in her 20s...", prediction: "Suggest food options", confidence: 0.98, latency_ms: 120 },
        { input: "User is a male commuter in his 40s...", prediction: "Optimize the route", confidence: 0.95, latency_ms: 95 },
        { input: "A couple on a date...", prediction: "Suggest events", confidence: 0.89, latency_ms: 150 },
      ];
      setReportData(mockReport);
      setTestResult("✅ テスト送信が完了しました（モック実行）");
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

  const handleDeleteDeployment = () => {
    console.log(`Deleting deployment: ${deployment.id}`);
    alert(`デプロイメント「${deployment.id}」を削除しました。(シミュレーション)`);
    router.push(`/${username}/${agentname}`);
  };

  // ★★★ any[] を TestReportEntry[] に修正 ★★★
  const convertToCSV = (data: TestReportEntry[]) => {
    if (!data || data.length === 0) return "";
    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => 
          JSON.stringify(row[header as keyof TestReportEntry], (key, value) => value === null ? '' : value)
        ).join(',')
      )
    ];
    return csvRows.join('\n');
  };

  const handleDownloadReport = () => {
    if (!reportData) return;
    const csvData = convertToCSV(reportData);
    const blob = new Blob([`\uFEFF${csvData}`], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `test-report-${deployment.id}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container mx-auto max-w-4xl p-6">
      {/* (UI部分は変更なし) */}
      <div className="mb-6">
        <h1 className="text-2xl font-normal">
          <Link href={`/${user.name}`} className="text-primary hover:underline">{user.name}</Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <Link href={`/${user.name}/${agent.name}`} className="text-primary hover:underline">{agent.name}</Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <span className="font-semibold">{deployment.id}</span>
        </h1>
      </div>
      <Card>
        <CardHeader><CardTitle>Deployment Details</CardTitle></CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-y-2">
            <div className="text-sm text-muted-foreground">Model ID</div>
            <div className="font-mono">{deployment.modelId}</div>
            <div className="text-sm text-muted-foreground">Status</div>
            <div><Badge variant={apiStatus === "active" ? "outline" : "secondary"}><span className={`mr-2 h-2 w-2 rounded-full ${apiStatus === "active" ? "bg-green-500" : "bg-gray-500"}`}></span>{apiStatus}</Badge></div>
            <div className="text-sm text-muted-foreground">Endpoint</div>
            <div className="font-mono text-xs break-all">{deployment.endpoint}</div>
            <div className="text-sm text-muted-foreground">Created At</div>
            <div>{new Date(deployment.createdAt).toLocaleString("ja-JP")}</div>
          </div>
          <div className="pt-2">
            <Button variant={apiStatus === "active" ? "destructive" : "default"} onClick={toggleApiStatus}><Power className="mr-2 h-4 w-4" />{apiStatus === "active" ? "Stop API" : "Start API"}</Button>
          </div>
          <div className="pt-6 border-t mt-4">
            <h3 className="font-semibold mb-2">Test with Text Data</h3>
            <p className="text-sm text-muted-foreground mb-4">Upload a Text file containing test data to simulate inference.</p>
            <div className="grid gap-3">
              <Label htmlFor="test-txt">Test File (.txt)</Label>
              <Input id="test-txt" type="file" accept=".txt" onChange={(e) => setSelectedFile(e.target.files?.[0] || null)} />
              {selectedFile && <p className="text-xs text-muted-foreground mt-1">選択中: {selectedFile.name}</p>}
              <Button onClick={handleTest} disabled={testing}><Upload className="mr-2 h-4 w-4" />{testing ? "Testing..." : "Start Test"}</Button>
              {testResult && (
                <div className="text-sm mt-3 border-t pt-3 flex flex-col sm:flex-row items-center justify-between gap-3">
                  <span className="text-muted-foreground">{testResult}</span>
                  {reportData && testResult.startsWith('✅') && (
                    <Button variant="outline" onClick={handleDownloadReport}><Download className="mr-2 h-4 w-4" />Download Report (.csv)</Button>
                  )}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
      <div className="mt-6">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Danger Zone</CardTitle>
            <CardDescription>この操作は元に戻すことができません。注意して実行してください。</CardDescription>
          </CardHeader>
          <CardContent>
            <AlertDialog>
              <AlertDialogTrigger asChild><Button variant="destructive"><Trash2 className="mr-2 h-4 w-4" />Delete This Deployment</Button></AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>本当に削除しますか？</AlertDialogTitle>
                  <AlertDialogDescription>デプロイメント <span className="font-mono font-semibold">{deployment.id}</span> を完全に削除します。この操作は取り消せません。</AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>キャンセル</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDeleteDeployment}>削除を実行</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}