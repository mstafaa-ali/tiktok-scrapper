"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, Loader2 } from "lucide-react";
import { useScraping } from "@/hooks/use-scraping";
import { toast } from "sonner";
import {
  scrapingFormSchema,
  type ScrapingFormValues,
} from "@/lib/validations/scraping";

interface ScrapingFormProps {
  onSuccess?: (jobId: string) => void;
}

export function ScrapingForm({ onSuccess }: ScrapingFormProps) {
  const scraping = useScraping();

  const form = useForm<ScrapingFormValues>({
    resolver: zodResolver(scrapingFormSchema),
    defaultValues: {
      videoUrl: "",
      maxComments: 100,
    },
  });

  async function onSubmit(values: ScrapingFormValues) {
    try {
      const result = await scraping.mutateAsync({
        video_url: values.videoUrl,
        max_comments: values.maxComments,
      });
      form.reset();
      toast.success("Scraping dimulai!", {
        description: `Job ID: ${result.job_id}`,
      });
      onSuccess?.(result.job_id);
    } catch {
      toast.error("Gagal memulai scraping", {
        description: "Silakan periksa URL dan coba lagi.",
      });
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Download className="h-5 w-5" />
          Scrape Video Comments
        </CardTitle>
        <CardDescription>
          Masukkan URL video TikTok untuk memulai scraping komentar.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="videoUrl" className="text-sm font-medium">
              Video URL
            </label>
            <Input
              id="videoUrl"
              placeholder="https://www.tiktok.com/@username/video/1234567890"
              {...form.register("videoUrl")}
              disabled={scraping.isPending}
            />
            {form.formState.errors.videoUrl && (
              <p className="text-sm text-destructive">
                {form.formState.errors.videoUrl.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="maxComments" className="text-sm font-medium">
              Jumlah Komentar
            </label>
            <Input
              id="maxComments"
              type="number"
              min={1}
              max={10000}
              placeholder="100"
              {...form.register("maxComments")}
              disabled={scraping.isPending}
            />
            {form.formState.errors.maxComments && (
              <p className="text-sm text-destructive">
                {form.formState.errors.maxComments.message}
              </p>
            )}
          </div>

          <Button type="submit" disabled={scraping.isPending} className="w-full">
            {scraping.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Memulai Scraping...
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Start Scraping
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
