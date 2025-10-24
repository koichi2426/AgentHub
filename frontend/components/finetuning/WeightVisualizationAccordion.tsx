"use client";
import { useState } from "react";
import Image from "next/image";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
// ★★★ data.tsから型をインポート ★★★
import type { Visualizations } from "@/lib/data";

type WeightVisualizationAccordionProps = {
  visualizations: Visualizations;
};

export default function WeightVisualizationAccordion({ visualizations }: WeightVisualizationAccordionProps) {
  const [selectedImage, setSelectedImage] = useState<{ url: string; name: string } | null>(null);

  const getDownloadFileName = (url: string, baseName: string) => {
    const extMatch = url.match(/\.(jpeg|jpg|gif|png)$/);
    const ext = extMatch ? extMatch[1] : 'png';
    const type = url.includes('before') ? '_before' : url.includes('after') ? '_after' : '_delta';
    return `${baseName}${type}.${ext}`;
  };

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
                <AccordionItem value={`item-${layerIndex}`} key={layer.layer_name}> {/* ✅ 修正: layerName -> layer_name */}
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

      <Dialog open={!!selectedImage} onOpenChange={(isOpen) => !isOpen && setSelectedImage(null)}>
        <DialogContent className="max-w-screen-lg p-6">
          <DialogHeader className="mb-4">
            <DialogTitle className="break-all">{selectedImage?.name}</DialogTitle>
          </DialogHeader>
          {selectedImage && (
            <div className="flex flex-col items-center gap-4">
              <Image src={selectedImage.url} alt="Enlarged view" width={1200} height={800} className="h-auto w-full rounded-md object-contain max-h-[80vh]"/>
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