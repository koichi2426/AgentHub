"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ArrowLeft, Bot, Calendar, CheckCircle, Clock, Download } from "lucide-react";
import Link from "next/link";

// ★★★ ここを修正しました ★★★
// 必要なモックJSONファイルのみをインポート
import agents from "@/lib/mocks/agents.json";
import jobs from "@/lib/mocks/finetuning_jobs.json";
import trainingDataLinks from "@/lib/mocks/training_data_links.json"; 
import weightVisualizationsData from "@/lib/mocks/weight_visualizations.json";

import { notFound } from "next/navigation";

type JobDetailPageProps = {
  params: {
    username: string;
    agentname: string;
    jobid: string;
  };
};

export default function JobDetailPage({ params }: JobDetailPageProps) {
  const [selectedImage, setSelectedImage] = useState<{ url: string; name: string } | null>(null);

  // ★★★ ここを修正しました ★★★
  // useMemoフック内で、全ての関連データをjobIdをキーに検索
  const { agent, job, trainingLink, visualizations } = useMemo(() => {
    const foundJob = jobs.find((j) => j.id === params.jobid);
    if (!foundJob) {
      return { agent: null, job: null, trainingLink: null, visualizations: null };
    }

    const foundAgent = agents.find(
      (a) =>
        a.id === foundJob.agentId &&
        a.owner.toLowerCase() === params.username.toLowerCase()
    );
    const foundTrainingLink = trainingDataLinks.find((d) => d.jobId === params.jobid);
    const foundVisualizations = weightVisualizationsData.find((v) => v.jobId === params.jobid);

    return { 
      agent: foundAgent, 
      job: foundJob, 
      trainingLink: foundTrainingLink,
      visualizations: foundVisualizations
    };
  }, [params.username, params.agentname, params.jobid]);

  // agentかjobが見つからなければ404ページを表示
  if (!agent || !job) {
    notFound();
  }

  const getDownloadFileName = (url: string, baseName: string) => {
    const extMatch = url.match(/\.(jpeg|jpg|gif|png)$/);
    const ext = extMatch ? extMatch[1] : 'png';
    const type = url.includes('before') ? '_before' : url.includes('after') ? '_after' : '_delta';
    return `${baseName}${type}.${ext}`;
  };

  return (
    <>
      <div className="container mx-auto max-w-4xl p-4 md:p-10">
        <div className="mb-8 flex flex-col gap-4">
          <Link href={`/${params.username}/${params.agentname}`} className="flex items-center text-sm text-muted-foreground hover:text-foreground">
            <ArrowLeft className="mr-2 h-4 w-4" />Back to {agent.name}
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Fine-tuning Job Details</h1>
            <p className="font-mono text-sm text-muted-foreground">{job.id}</p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <Card className="md:col-span-1">
            <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
            <CardContent className="space-y-4 text-sm">
                <div className="flex items-center">
                    <Bot className="mr-3 h-5 w-5 text-muted-foreground" />
                    <div><p className="font-semibold">{job.modelId}</p><p className="text-xs text-muted-foreground">Model ID</p></div>
                </div>
                <div className="flex items-center">
                    <CheckCircle className="mr-3 h-5 w-5 text-muted-foreground" />
                    <Badge variant={job.status === "completed" ? "default" : "secondary"}>{job.status}</Badge>
                </div>
                <div className="flex items-center">
                    <Calendar className="mr-3 h-5 w-5 text-muted-foreground" />
                    <div><p>{new Date(job.createdAt).toLocaleString("ja-JP")}</p><p className="text-xs text-muted-foreground">Created At</p></div>
                </div>
                {job.finishedAt && (
                    <div className="flex items-center">
                    <Clock className="mr-3 h-5 w-5 text-muted-foreground" />
                    <div><p>{new Date(job.finishedAt).toLocaleString("ja-JP")}</p><p className="text-xs text-muted-foreground">Finished At</p></div>
                    </div>
                )}
            </CardContent>
          </Card>
          
          {/* ★★★ ここを修正しました ★★★ */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Training Data Used</CardTitle>
              <CardDescription>
                Click the button below to download the training data used for this job.
              </CardDescription>
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
                <p className="text-sm text-muted-foreground">
                  Training data is not available for this job.
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* ★★★ ここを修正しました ★★★ */}
        {/* visualizationsデータが存在する場合のみ、このセクションを表示 */}
        {visualizations && (
          <div className="mt-6">
            <Card>
              <CardHeader><CardTitle>Weight Change Visualization</CardTitle><CardDescription>Click on an image to enlarge.</CardDescription></CardHeader>
              <CardContent>
                <Accordion type="single" collapsible defaultValue="item-0">
                  {visualizations.layers.map((layer, layerIndex) => (
                    <AccordionItem value={`item-${layerIndex}`} key={layer.layerName}>
                      <AccordionTrigger className="text-lg">Layer {layerIndex}</AccordionTrigger>
                      <AccordionContent>
                        <div className="flex flex-col gap-8">
                          {layer.weights.map((weight) => (
                            <div key={weight.name}>
                              <p className="mb-2 break-all font-mono text-xs text-muted-foreground">{weight.name}</p>
                              <div className="flex flex-col items-center justify-around gap-4 md:flex-row">
                                <div className="flex flex-col items-center gap-2">
                                  <p className="font-semibold">Before</p>
                                  <div className="cursor-pointer" onClick={() => setSelectedImage({ url: weight.before, name: weight.name })}><Image src={weight.before} alt={`Before: ${weight.name}`} width={200} height={200} className="rounded-md border" /></div>
                                </div>
                                <div className="flex flex-col items-center gap-2">
                                  <p className="font-semibold">After</p>
                                  <div className="cursor-pointer" onClick={() => setSelectedImage({ url: weight.after, name: weight.name })}><Image src={weight.after} alt={`After: ${weight.name}`} width={200} height={200} className="rounded-md border" /></div>
                                </div>
                                <div className="flex flex-col items-center gap-2">
                                  <p className="font-semibold">Delta</p>
                                  <div className="cursor-pointer" onClick={() => setSelectedImage({ url: weight.delta, name: weight.name })}><Image src={weight.delta} alt={`Delta: ${weight.name}`} width={200} height={200} className="rounded-md border" /></div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      <Dialog open={!!selectedImage} onOpenChange={(isOpen) => !isOpen && setSelectedImage(null)}>
        <DialogContent className="max-w-screen-lg p-6">
          <DialogHeader className="mb-4">
            <DialogTitle className="break-all">{selectedImage?.name}</DialogTitle>
          </DialogHeader>
          {selectedImage && (
            <div className="flex flex-col items-center gap-4">
              <Image src={selectedImage.url} alt="Enlarged view" width={1200} height={800} className="h-auto w-full rounded-md object-contain max-h-[80vh]"/>
              <a 
                href={selectedImage.url} 
                download={getDownloadFileName(selectedImage.url, selectedImage.name)}
                className="w-full sm:w-auto"
              >
                <Button className="w-full"><Download className="mr-2 h-4 w-4" />Download Image</Button>
              </a>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}