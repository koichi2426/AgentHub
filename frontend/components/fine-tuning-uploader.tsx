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

/**
 * fine-tuning-uploader.tsx
 * Triplet JSONL ファイルを選択し、/api/finetuning に送信するコンポーネント
 */
export default function FineTuningUploader({
  agentId,
}: {
  agentId: string;
}) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("JSONLファイルを選択してください。");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("agentId", agentId);

      const res = await fetch("/api/finetuning", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("アップロードに失敗しました");

      alert("ジョブを送信しました。");
      setSelectedFile(null);
    } catch (e: any) {
      alert(e.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit New Fine-tuning Job</CardTitle>
        <CardDescription>
          Upload a JSONL file containing triplet data for fine-tuning.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid w-full gap-2">
          <Label htmlFor="triplet-file">Triplet JSONL File</Label>
          <Input
            id="triplet-file"
            type="file"
            accept=".jsonl"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          />
          {selectedFile && (
            <p className="text-sm text-muted-foreground mt-1">
              選択中: {selectedFile.name}
            </p>
          )}
        </div>
        <Button onClick={handleUpload} disabled={uploading}>
          <Rocket className="mr-2 h-4 w-4" />
          {uploading ? "Uploading..." : "Start Job"}
        </Button>
      </CardContent>
    </Card>
  );
}
