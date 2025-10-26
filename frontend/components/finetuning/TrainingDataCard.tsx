"use client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
// FinetuningJob 型をインポート
import type { FinetuningJob } from "@/lib/data";

type TrainingDataCardProps = {
  // Prop を FinetuningJob に変更 (null/undefined も許容)
  job: FinetuningJob | undefined | null; 
};

export default function TrainingDataCard({ job }: TrainingDataCardProps) {

  // ファイル名を取得するヘルパー関数 (パスからファイル名部分を抽出)
  const getFileNameFromPath = (path: string | undefined | null): string | undefined => {
    if (!path) return undefined;
    return path.split('/').pop();
  };

  const fileName = getFileNameFromPath(job?.training_file_path);

  // ダウンロードボタンがクリックされたときの処理 (API呼び出しを実装する必要あり)
  const handleDownloadClick = () => {
    if (job && fileName) {
      console.log(`Downloading file for job ${job.id}: ${fileName}`);
      // TODO: ここでバックエンドのダウンロードAPIを呼び出す
      // 例: fetch(`/api/v1/jobs/${job.id}/download`).then(...)
      alert(`ファイル「${fileName}」のダウンロードを開始します。(API未実装)`);
    }
  };

  return (
    <Card className="md:col-span-2">
      <CardHeader>
        <CardTitle>Training Data Used</CardTitle>
        <CardDescription>
          {fileName 
            ? `Click the button below to download the training data used for this job (${fileName}).`
            : "Training data information is not available for this job."}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex h-full items-center justify-center pt-2">
        {job && fileName ? (
          // href と download 属性は削除し、onClick で処理
          <Button className="w-full sm:w-auto" onClick={handleDownloadClick}>
            <Download className="mr-2 h-4 w-4" />
            Download Training Data ({fileName.split('.').pop()})
          </Button>
        ) : (
          <p className="text-sm text-muted-foreground">Training data path is not available.</p>
        )}
      </CardContent>
    </Card>
  );
}