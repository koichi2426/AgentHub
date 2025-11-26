"use client";

import { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Upload,
  Download,
  Cpu,
  CheckCircle,
  XCircle,
} from "lucide-react";

import { DeploymentTestResponse } from "@/lib/data";

type DeploymentTestCardProps = {
  deploymentId: string;
  onRunTest: (testFile: File) => Promise<void>;
  testResult: DeploymentTestResponse | null;
  isTestLoading: boolean;
  errorMessage: string | null;
};

export default function DeploymentTestCard({
  deploymentId,
  onRunTest,
  testResult,
  isTestLoading,
  errorMessage,
}: DeploymentTestCardProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleTest = () => {
    if (!selectedFile) {
      alert("TXTファイルを選択してください。");
      return;
    }
    onRunTest(selectedFile);
  };

  const handleDownloadReport = () => {
    if (!testResult) return;

    // APIレスポンスをそのままJSON形式でダウンロード
    const jsonContent = JSON.stringify(testResult, null, 2);

    const blob = new Blob([jsonContent], {
      type: "application/json;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `deployment-report-${deploymentId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const metrics = testResult?.test_result.overall_metrics;
  const isSuccess = !!testResult && !isTestLoading && !errorMessage;

  return (
    <Card className="relative mt-6 overflow-hidden">
      {isTestLoading && (
        <div className="absolute inset-0 bg-white/70 backdrop-blur-sm flex flex-col items-center justify-center z-20">
          <Cpu className="h-8 w-8 animate-spin text-primary mb-2" />
          <p className="text-sm text-gray-600 animate-pulse">
            Running inference test...
          </p>
        </div>
      )}

      <CardHeader>
        <CardTitle>Test Deployment</CardTitle>
        <CardDescription>
          Upload a tab-separated (.txt) test data file to simulate model
          inference.
        </CardDescription>
      </CardHeader>

      <CardContent className={isTestLoading ? "opacity-50 pointer-events-none" : ""}>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="test-txt">Test File (.txt)</Label>
            <Input
              id="test-txt"
              type="file"
              accept=".txt"
              onChange={(e) =>
                setSelectedFile(e.target.files?.[0] || null)
              }
            />
            {selectedFile && (
              <p className="text-xs text-muted-foreground mt-1">
                選択中: {selectedFile.name}
              </p>
            )}
          </div>

          <Button
            onClick={handleTest}
            disabled={isTestLoading || !selectedFile}
          >
            {isTestLoading ? (
              <>
                <Cpu className="mr-2 h-4 w-4 animate-spin" />
                Running Inference Test...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Start Test
              </>
            )}
          </Button>

          {errorMessage && (
            <div className="text-sm mt-3 pt-3 text-red-500 flex items-center">
              <XCircle className="mr-2 h-4 w-4" />
              API Error: {errorMessage}
            </div>
          )}

          {isSuccess && metrics && (
            <div className="mt-4 border-t pt-4 transition-all duration-300 ease-in-out">
              <h4 className="text-lg font-semibold flex items-center mb-4 text-green-600">
                <CheckCircle className="mr-2 h-5 w-5" />
                Test Completed
              </h4>

              <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <p className="font-medium text-muted-foreground">Total Cases:</p>
                <p className="font-medium">{metrics.total_test_cases ?? 0}</p>

                <p className="font-medium text-muted-foreground">Correct:</p>
                <p className="font-medium">{metrics.correct_predictions ?? 0}</p>

                <p className="font-medium text-muted-foreground">Accuracy:</p>
                <p className="font-bold text-lg text-primary">
                  {((metrics.accuracy ?? 0) * 100).toFixed(2)}%
                </p>

                <p className="font-medium text-muted-foreground">Avg Latency:</p>
                <p className="font-medium">{(metrics.latency_ms ?? 0).toFixed(2)} ms</p>

                <p className="font-medium text-muted-foreground">Avg Cost:</p>
                <p className="font-medium text-red-500">
                  {(metrics.cost_estimate_mwh ?? 0).toFixed(4)} mWh
                  <span className="text-muted-foreground ml-2">
                    ({(metrics.cost_estimate_mj ?? 0).toFixed(6)} mJ)
                  </span>
                </p>

                <p className="font-medium text-muted-foreground">Average Gross Energy:</p>
                <p className="font-medium text-blue-500">
                  {(metrics.average_gross_mj ?? 0).toFixed(6)} mJ {/* ★★★ 修正 */}
                </p>
              </div>

              <div className="mt-4 flex justify-end">
                <Button variant="outline" onClick={handleDownloadReport}>
                  <Download className="mr-2 h-4 w-4" />
                  Download Full Report (.json)
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
