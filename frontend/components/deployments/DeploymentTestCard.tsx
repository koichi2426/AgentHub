"use client";
import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Upload, Download } from "lucide-react";

type TestReportEntry = {
  input: string;
  prediction: string;
  confidence: number;
  latency_ms: number;
};

type DeploymentTestCardProps = {
  deploymentId: string;
};

export default function DeploymentTestCard({ deploymentId }: DeploymentTestCardProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [reportData, setReportData] = useState<TestReportEntry[] | null>(null);

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
      ];
      setReportData(mockReport);
      setTestResult("✅ テスト送信が完了しました（モック実行）");
    } catch (err: unknown) {
      if (err instanceof Error) setTestResult(`❌ Error: ${err.message}`);
      else setTestResult("❌ Unknown error occurred.");
    } finally {
      setTesting(false);
    }
  };

  const convertToCSV = (data: TestReportEntry[]) => {
    if (!data || data.length === 0) return "";
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(','), ...data.map(row => headers.map(header => JSON.stringify(row[header as keyof TestReportEntry])).join(','))];
    return csvRows.join('\n');
  };

  const handleDownloadReport = () => {
    if (!reportData) return;
    const csvData = convertToCSV(reportData);
    const blob = new Blob([`\uFEFF${csvData}`], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `test-report-${deploymentId}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>Test Deployment</CardTitle>
        <CardDescription>Upload a Text file containing test data to simulate inference.</CardDescription>
      </CardHeader>
      <CardContent>
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
      </CardContent>
    </Card>
  );
}