"use client";

import { useState } from "react";
import { ScrapingForm } from "@/features/scraping/scraping-form";
import { ScrapeProgress } from "@/features/scraping/scrape-progress";
import { ScrapeHistory } from "@/features/scraping/scrape-history";

export function ScrapingClient() {
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Scraping</h1>
        <p className="text-muted-foreground">
          Masukkan URL video TikTok untuk mengambil komentar.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Form */}
        <div className="space-y-4">
          <ScrapingForm onSuccess={(jobId) => setActiveJobId(jobId)} />

          {/* Progress */}
          {activeJobId && <ScrapeProgress jobId={activeJobId} />}
        </div>

        {/* History */}
        <ScrapeHistory />
      </div>
    </div>
  );
}
