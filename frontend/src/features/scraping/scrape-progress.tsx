"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";
import { useJob } from "@/hooks/use-jobs";
import type { JobStatus } from "@/types/job";

interface ScrapeProgressProps {
  jobId: string;
}

function StatusIcon({ status }: { status: JobStatus }) {
  switch (status) {
    case "PENDING":
      return <Clock className="h-4 w-4" />;
    case "RUNNING":
      return <Loader2 className="h-4 w-4 animate-spin" />;
    case "SUCCESS":
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case "FAILED":
      return <XCircle className="h-4 w-4 text-destructive" />;
  }
}

function StatusBadge({ status }: { status: JobStatus }) {
  const variant =
    status === "SUCCESS"
      ? "default"
      : status === "FAILED"
        ? "destructive"
        : "secondary";

  return (
    <Badge variant={variant} className="flex items-center gap-1">
      <StatusIcon status={status} />
      {status}
    </Badge>
  );
}

export function ScrapeProgress({ jobId }: ScrapeProgressProps) {
  const { data: job, isLoading, isError } = useJob(jobId);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-6">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span className="ml-2">Memuat status job...</span>
        </CardContent>
      </Card>
    );
  }

  if (isError || !job) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-sm text-destructive">Gagal memuat status job.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-base">
          Job Progress
          <StatusBadge status={job.status} />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Job ID:</span>
            <p className="font-mono text-xs">{job.id}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Video URL:</span>
            <p className="truncate text-xs">{job.video_url}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Comments Scraped:</span>
            <p className="font-bold">{job.comments_scraped.toLocaleString()}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Started:</span>
            <p className="text-xs">
              {new Date(job.started_at).toLocaleString("id-ID")}
            </p>
          </div>
        </div>

        {job.error_message && (
          <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            {job.error_message}
          </div>
        )}

        {job.status === "RUNNING" && (
          <p className="text-xs text-muted-foreground animate-pulse">
            Auto-polling setiap 5 detik...
          </p>
        )}
      </CardContent>
    </Card>
  );
}
