"use client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
// ★★★ data.tsから型をインポート ★★★
import type { TrainingLink } from "@/lib/data";

type TrainingDataCardProps = {
  // ★★★ undefined も許容するように修正 ★★★
  trainingLink: TrainingLink | undefined;
};

export default function TrainingDataCard({ trainingLink }: TrainingDataCardProps) {
  return (
    <Card className="md:col-span-2">
      <CardHeader>
        <CardTitle>Training Data Used</CardTitle>
        <CardDescription>Click the button below to download the training data used for this job.</CardDescription>
      </CardHeader>
      <CardContent className="flex h-full items-center justify-center pt-2">
        {trainingLink && trainingLink.dataUrl ? (
          <a href={trainingLink.dataUrl} download={trainingLink.fileName || true}>
            <Button className="w-full sm:w-auto">
              <Download className="mr-2 h-4 w-4" />
              Download Training Data ({trainingLink.fileName?.split('.').pop()})
            </Button>
          </a>
        ) : (
          <p className="text-sm text-muted-foreground">Training data is not available for this job.</p>
        )}
      </CardContent>
    </Card>
  );
}