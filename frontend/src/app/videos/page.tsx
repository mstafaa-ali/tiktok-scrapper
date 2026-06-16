import type { Metadata } from "next";
import { VideosClient } from "./_components/videos-client";
import { Suspense } from "react";
import { PageSkeleton } from "@/components/ui/page-skeleton";

export const metadata: Metadata = {
  title: "Videos | TikTok Scraper",
  description: "Daftar video TikTok yang telah di-scrape",
};

export default function VideosPage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <VideosClient />
    </Suspense>
  );
}
