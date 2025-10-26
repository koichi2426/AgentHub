"use client";
import { useState } from "react";
import Image from "next/image";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
// ★★★ data.tsから型をインポート ★★★
import type { Visualizations, WeightVisualizationDetail } from "@/lib/data";

// NOTE: WeightVisualizationDetail 型は、JobDetailPageでURL変換後に
// before_url, after_url, delta_url が完全な画像URLを持つことを想定しています。

type WeightVisualizationAccordionProps = {
  visualizations: Visualizations;
};

// ダウンロードファイル名を取得するヘルパー関数
const getDownloadFileName = (url: string, baseName: string) => {
    // URLにプロキシパスが含まれているため、ファイル名部分を抽出して整形
    const filenameMatch = url.match(/[^/]+$/);
    const filename = filenameMatch ? filenameMatch[0] : 'download';

    const extMatch = filename.match(/\.(jpeg|jpg|gif|png)$/);
    const ext = extMatch ? extMatch[1] : 'png';
    // ファイル名からbefore, after, deltaを判定
    const type = filename.includes('before') ? '_before' : filename.includes('after') ? '_after' : '_delta';
    
    // ベース名とタイプ、拡張子を結合して安全なファイル名にする
    return `${baseName.replace(/\./g, '_')}${type}.${ext}`;
};

export default function WeightVisualizationAccordion({ visualizations }: WeightVisualizationAccordionProps) {
  // selectedImage.url は完全な画像URL (http://localhost:8000/v1/visuals/...)
  const [selectedImage, setSelectedImage] = useState<{ url: string; name: string } | null>(null);

  // DTOの型に合わせたプロパティ名を内部で使用するためのカスタムタイプアサーション
  // ※バックエンドのDTOとフロントエンドのdata.tsの型定義が一致していることを前提とします
  type WeightDetailWithUrls = WeightVisualizationDetail & { before_url: string; after_url: string; delta_url: string };

  return (
    <>
      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle>Weight Change Visualization</CardTitle>
            <CardDescription>Click on an image to enlarge.</CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible defaultValue="item-0">
              {visualizations.layers.map((layer, layerIndex) => (
                <AccordionItem value={`item-${layerIndex}`} key={layer.layer_name}>
                  <AccordionTrigger className="text-lg">Layer {layerIndex}</AccordionTrigger>
                  <AccordionContent>
                    <div className="flex flex-col gap-8">
                      {layer.weights.map((weight: WeightDetailWithUrls) => (
                        <div key={weight.name}>
                          <p className="mb-2 break-all font-mono text-xs text-muted-foreground">{weight.name}</p>
                          <div className="flex flex-col items-center justify-around gap-4 md:flex-row">
                            
                            {/* BEFORE 画像 */}
                            <div className="flex flex-col items-center gap-2">
                              <p className="font-semibold">Before</p>
                              <div 
                                className="cursor-pointer" 
                                onClick={() => setSelectedImage({ url: weight.before_url, name: weight.name })}>
                                <Image 
                                  src={weight.before_url} 
                                  alt={`Before: ${weight.name}`} 
                                  width={200} 
                                  height={200} 
                                  className="rounded-md border" 
                                  unoptimized // ★★★ プロキシ経由で動的なため最適化を無効化 ★★★
                                />
                              </div>
                            </div>
                            
                            {/* AFTER 画像 */}
                            <div className="flex flex-col items-center gap-2">
                              <p className="font-semibold">After</p>
                              <div 
                                className="cursor-pointer" 
                                onClick={() => setSelectedImage({ url: weight.after_url, name: weight.name })}>
                                <Image 
                                  src={weight.after_url} 
                                  alt={`After: ${weight.name}`} 
                                  width={200} 
                                  height={200} 
                                  className="rounded-md border" 
                                  unoptimized // ★★★ プロキシ経由で動的なため最適化を無効化 ★★★
                                />
                              </div>
                            </div>
                            
                            {/* DELTA 画像 */}
                            <div className="flex flex-col items-center gap-2">
                              <p className="font-semibold">Delta</p>
                              <div 
                                className="cursor-pointer" 
                                onClick={() => setSelectedImage({ url: weight.delta_url, name: weight.name })}>
                                <Image 
                                  src={weight.delta_url} 
                                  alt={`Delta: ${weight.name}`} 
                                  width={200} 
                                  height={200} 
                                  className="rounded-md border" 
                                  unoptimized // ★★★ プロキシ経由で動的なため最適化を無効化 ★★★
                                />
                              </div>
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

      <Dialog open={!!selectedImage} onOpenChange={(isOpen) => !isOpen && setSelectedImage(null)}>
        <DialogContent className="max-w-screen-lg p-6">
          <DialogHeader className="mb-4">
            <DialogTitle className="break-all">{selectedImage?.name}</DialogTitle>
          </DialogHeader>
          {selectedImage && (
            <div className="flex flex-col items-center gap-4">
              <Image 
                src={selectedImage.url} 
                alt="Enlarged view" 
                width={1200} 
                height={800} 
                className="h-auto w-full rounded-md object-contain max-h-[80vh]"
                unoptimized // ★★★ プロキシ経由で動的なため最適化を無効化 ★★★
              />
              <a href={selectedImage.url} download={getDownloadFileName(selectedImage.url, selectedImage.name)} className="w-full sm:w-auto">
                <Button className="w-full"><Download className="mr-2 h-4 w-4" />Download Image</Button>
              </a>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}