import type { Metadata } from "next";
import { ScrapingClient } from "./_components/scraping-client";
import { Suspense } from "react";
import { PageSkeleton } from "@/components/ui/page-skeleton";

export const metadata: Metadata = {
  title: "Scraping | TikTok Scraper",
  description: "Mulai scraping komentar dari video TikTok",
};

export default function ScrapingPage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
        <ScrapingClient />
    </Suspense>
  );
}
