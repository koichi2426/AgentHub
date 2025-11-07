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
    const { overall_metrics, case_results } = testResult.test_result;

    const headers = [
      "ID",
      "Input Data",
      "Expected Output",
      "Predicted Output",
      "Is Correct",
    ];

    const csvRows = case_results.map((caseResult) => {
      return [
        caseResult.id,
        JSON.stringify(caseResult.input_data),
        JSON.stringify(caseResult.expected_output),
        JSON.stringify(caseResult.predicted_output),
        caseResult.is_correct ? "TRUE" : "FALSE",
      ].join(",");
    });

    const overallSummary = [
      ["Overall Accuracy:", overall_metrics.accuracy.toFixed(4)],
      ["Average Latency (ms):", overall_metrics.latency_ms.toFixed(3)],
      ["Average Cost (mWh):", overall_metrics.cost_estimate_mwh.toFixed(4)],
      ["Total Cases:", overall_metrics.total_test_cases],
      ["Correct Predictions:", overall_metrics.correct_predictions],
    ]
      .map((row) => row.join(","))
      .join("\n");

    const csvContent = [
      `Deployment Test Report - Deployment ID: ${deploymentId}`,
      overallSummary,
      "\n--- Detailed Case Results ---",
      headers.join(","),
      ...csvRows,
    ].join("\n");

    const blob = new Blob([`\uFEFF${csvContent}`], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `deployment-report-${deploymentId}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const metrics = testResult?.test_result.overall_metrics;
  const isSuccess = !!testResult && !isTestLoading && !errorMessage;

  return (
    <Card className="relative mt-6 overflow-hidden">
      {/* --- ローディング中のオーバーレイ --- */}
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
          {/* --- ファイル選択 --- */}
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

          {/* --- 実行ボタン --- */}
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

          {/* --- エラー表示 --- */}
          {errorMessage && (
            <div className="text-sm mt-3 pt-3 text-red-500 flex items-center">
              <XCircle className="mr-2 h-4 w-4" />
              API Error: {errorMessage}
            </div>
          )}

          {/* --- 成功結果表示 --- */}
          {isSuccess && metrics && (
            <div className="mt-4 border-t pt-4 transition-all duration-300 ease-in-out">
              <h4 className="text-lg font-semibold flex items-center mb-4 text-green-600">
                <CheckCircle className="mr-2 h-5 w-5" />
                Test Completed
              </h4>

              <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <p className="font-medium text-muted-foreground">
                  Total Cases:
                </p>
                <p className="font-medium">{metrics.total_test_cases}</p>

                <p className="font-medium text-muted-foreground">Correct:</p>
                <p className="font-medium">{metrics.correct_predictions}</p>

                <p className="font-medium text-muted-foreground">Accuracy:</p>
                <p className="font-bold text-lg text-primary">
                  {(metrics.accuracy * 100).toFixed(2)}%
                </p>

                <p className="font-medium text-muted-foreground">
                  Avg Latency:
                </p>
                <p className="font-medium">
                  {metrics.latency_ms.toFixed(2)} ms
                </p>

                <p className="font-medium text-muted-foreground">Avg Cost:</p>
                <p className="font-medium text-red-500">
                  {metrics.cost_estimate_mwh.toFixed(4)} mWh
                </p>
              </div>

              <div className="mt-4 flex justify-end">
                <Button variant="outline" onClick={handleDownloadReport}>
                  <Download className="mr-2 h-4 w-4" />
                  Download Full Report (.csv)
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
