"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download, Loader2, Sparkles, TrendingUp, Users, MessageCircle } from "lucide-react";
import { useScraping } from "@/hooks/use-scraping";
import { toast } from "sonner";
import {
  scrapingFormSchema,
  type ScrapingFormValues,
} from "@/lib/validations/scraping";
import { useRouter } from "next/navigation";

export function HeroScrapeForm() {
  const scraping = useScraping();
  const router = useRouter();

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
      toast.success("Scraping started successfully!", {
        description: `Job ID: ${result.job_id}`,
      });
      // Arahkan ke halaman jobs atau tampilkan progress
      router.push("/jobs");
    } catch {
      toast.error("Failed to start scraping", {
        description: "Please check the URL and try again.",
      });
    }
  }

  return (
    <div className="relative w-full max-w-4xl mx-auto mt-12 mb-20 animate-fade-in">
      {/* Decorative blobs */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-primary/30 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-pulse" />
      <div className="absolute top-0 -right-4 w-72 h-72 bg-accent/30 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-pulse delay-700" />
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-secondary/30 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-pulse delay-1000" />

      <div className="relative glass p-8 md:p-12 rounded-3xl border border-border/50 shadow-2xl backdrop-blur-xl flex flex-col items-center text-center space-y-8 z-10">
        
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary font-medium text-sm border border-primary/20">
          <Sparkles className="w-4 h-4" />
          <span>Advanced TikTok Comment Scraper</span>
        </div>

        <div className="space-y-4 max-w-2xl">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-foreground">
            Extract Insights from <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">TikTok</span> Videos
          </h1>
          <p className="text-lg text-muted-foreground">
            Instantly scrape comments, analyze engagement, and understand your audience with our powerful scraping tool.
          </p>
        </div>

        <form onSubmit={form.handleSubmit(onSubmit)} className="w-full max-w-2xl relative">
          <div className="relative flex items-center">
            <Input
              id="videoUrl"
              placeholder="Paste TikTok video URL here..."
              className="pl-6 pr-40 h-16 md:h-20 text-lg md:text-xl rounded-full bg-background/80 border-2 border-border/50 focus-visible:ring-primary focus-visible:border-primary shadow-inner transition-all"
              {...form.register("videoUrl")}
              disabled={scraping.isPending}
            />
            <div className="absolute right-2 md:right-3">
              <Button 
                type="submit" 
                size="lg" 
                disabled={scraping.isPending} 
                className="h-12 md:h-14 px-6 md:px-8 rounded-full text-base font-semibold shadow-lg transition-transform hover:scale-105"
              >
                {scraping.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Processing
                  </>
                ) : (
                  <>
                    <Download className="mr-2 h-5 w-5" />
                    Start Scrape
                  </>
                )}
              </Button>
            </div>
          </div>
          {form.formState.errors.videoUrl && (
            <p className="absolute -bottom-6 left-6 text-sm font-medium text-destructive">
              {form.formState.errors.videoUrl.message}
            </p>
          )}
          <div className="mt-8 flex flex-col items-center justify-center gap-2">
            <div className="flex items-center gap-4">
              <label htmlFor="maxCommentsHero" className="text-sm font-medium text-muted-foreground">
                Batas Komentar:
              </label>
              <Input
                id="maxCommentsHero"
                type="number"
                min={1}
                max={10000}
                className="w-24 bg-background/80 text-center border-2 border-border/50"
                {...form.register("maxComments", { valueAsNumber: true })}
                disabled={scraping.isPending}
              />
            </div>
            {form.formState.errors.maxComments && (
              <p className="text-sm font-medium text-destructive">
                {form.formState.errors.maxComments.message}
              </p>
            )}
          </div>
        </form>

        <div className="grid grid-cols-3 gap-4 md:gap-8 w-full max-w-2xl mt-8 pt-8 border-t border-border/50">
          <div className="flex flex-col items-center justify-center gap-2">
            <div className="p-3 bg-primary/10 rounded-2xl text-primary">
              <MessageCircle className="w-6 h-6" />
            </div>
            <span className="text-sm font-medium text-muted-foreground">Unlimited Comments</span>
          </div>
          <div className="flex flex-col items-center justify-center gap-2">
            <div className="p-3 bg-accent/10 rounded-2xl text-accent">
              <TrendingUp className="w-6 h-6" />
            </div>
            <span className="text-sm font-medium text-muted-foreground">Real-time Analysis</span>
          </div>
          <div className="flex flex-col items-center justify-center gap-2">
            <div className="p-3 bg-secondary/10 rounded-2xl text-secondary-foreground">
              <Users className="w-6 h-6" />
            </div>
            <span className="text-sm font-medium text-muted-foreground">Audience Insights</span>
          </div>
        </div>

      </div>
    </div>
  );
}
