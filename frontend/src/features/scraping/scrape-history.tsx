"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useJobs } from "@/hooks/use-jobs";
import Link from "next/link";
import type { JobStatus } from "@/types/job";

function getStatusVariant(status: JobStatus) {
  switch (status) {
    case "SUCCESS":
      return "default" as const;
    case "FAILED":
      return "destructive" as const;
    case "RUNNING":
      return "secondary" as const;
    default:
      return "outline" as const;
  }
}

export function ScrapeHistory() {
  const { data, isLoading } = useJobs({
    page: 1,
    page_size: 5,
    sort_by: "created_at",
    sort_order: "desc",
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Riwayat Scraping</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-14" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Riwayat Scraping</CardTitle>
        <Link
          href="/jobs"
          className="text-sm text-primary hover:underline"
        >
          Lihat semua →
        </Link>
      </CardHeader>
      <CardContent>
        {data && data.data.length > 0 ? (
          <div className="space-y-3">
            {data.data.map((job) => (
              <div
                key={job.id}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div className="space-y-1">
                  <p className="text-sm truncate max-w-[200px]">
                    {job.video_url}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(job.created_at).toLocaleString("id-ID")}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">
                    {job.comments_scraped}
                  </span>
                  <Badge variant={getStatusVariant(job.status)}>
                    {job.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Belum ada riwayat scraping.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
