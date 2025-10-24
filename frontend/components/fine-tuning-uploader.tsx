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
import { Rocket } from "lucide-react";

// ★★★ [新規追加] Fetcher関数のインポート ★★★
import { createFinetuningJob } from "@/fetchs/create_finetuning_job/create_finetuning_job";
import Cookies from "js-cookie";

/**
 * fine-tuning-uploader.tsx
 * テキストファイルを選択し、/v1/agents/{agentId}/finetuning に送信するコンポーネント
 */
export default function FineTuningUploader({
  agentId,
}: {
  agentId: string;
}) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (): Promise<void> => {
    if (!selectedFile) {
      alert("トレーニングデータファイルを選択してください。"); // アラートメッセージを修正
      return;
    }

    const token = Cookies.get("auth_token");
    if (!token) {
        alert("認証トークンが見つかりません。再ログインしてください。");
        return;
    }

    setUploading(true);
    try {
      // ★★★ Fetcher関数への引数を構築 ★★★
      const requestData = {
          trainingFile: selectedFile,
      };
      
      // agentId は string 型で受け取っているため、number に変換
      const numericAgentId = parseInt(agentId, 10);
      if (isNaN(numericAgentId)) {
           throw new Error("Invalid Agent ID format.");
      }

      // ★★★ 新しい Fetcher を使用して API を呼び出す ★★★
      const result = await createFinetuningJob(
        requestData,
        numericAgentId,
        token
      );

      // 成功レスポンスのメッセージを表示
      alert(`ジョブID ${result.id} をキューに送信しました: ${result.message}`);
      setSelectedFile(null);

    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "予期しないエラーが発生しました。";
      alert(`送信失敗: ${message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit New Fine-tuning Job</CardTitle>
        <CardDescription>
          Upload a Text file containing training data for fine-tuning.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid w-full gap-2">
          <Label htmlFor="training-data-file">Training Data File (.txt)</Label>
          <Input
            id="training-data-file"
            type="file"
            accept=".txt"
            onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
          />
          {selectedFile && (
            <p className="text-sm text-muted-foreground mt-1">
              選択中: {selectedFile.name}
            </p>
          )}
        </div>
        <Button onClick={handleUpload} disabled={uploading || !selectedFile}>
          <Rocket className="mr-2 h-4 w-4" />
          {uploading ? "Uploading..." : "Start Job"}
        </Button>
      </CardContent>
    </Card>
  );
}