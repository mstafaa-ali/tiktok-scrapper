import type { Metadata } from "next";
import { JobsClient } from "./_components/jobs-client";
import { Suspense } from "react";
import { PageSkeleton } from "@/components/ui/page-skeleton";

export const metadata: Metadata = {
  title: "Job Monitoring | TikTok Scraper",
  description: "Pantau status scraping jobs",
};

export default function JobsPage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
        <JobsClient />
    </Suspense>
  );
}
