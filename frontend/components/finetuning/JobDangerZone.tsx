"use client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Trash2 } from "lucide-react";

type JobDangerZoneProps = {
  // ★★★ 修正: modelId を model_id: string | null に変更 ★★★
  job: { model_id: string | null };
  onDelete: () => void;
};

export default function JobDangerZone({ job, onDelete }: JobDangerZoneProps) {
  // job.model_id が null の場合は、削除対象を '未生成モデル' などとして扱う
  const modelIdentifier = job.model_id || "未生成モデル (ジョブデータのみ)";

  return (
    <div className="mt-6">
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>この操作は元に戻すことができません。注意して実行してください。</CardDescription>
        </CardHeader>
        <CardContent>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button 
                variant="destructive"
                // モデルIDがない場合、ボタンを無効化することも検討できますが、ここでは削除対象を明記
                // disabled={!job.model_id} 
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete This Model
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>本当に削除しますか？</AlertDialogTitle>
                <AlertDialogDescription>
                  モデル <span className="font-mono font-semibold">{modelIdentifier}</span> を完全に削除します。この操作は取り消せません。
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>キャンセル</AlertDialogCancel>
                <AlertDialogAction onClick={onDelete}>
                  削除を実行
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>
    </div>
  );
}