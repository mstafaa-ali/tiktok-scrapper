"use client";

import { DataTable, type Column } from "@/components/tables/data-table";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";
import type { ScrapeJob, JobStatus } from "@/types/job";

function StatusBadge({ status }: { status: JobStatus }) {
  const config = {
    PENDING: {
      variant: "outline" as const,
      icon: Clock,
      className: "",
    },
    RUNNING: {
      variant: "secondary" as const,
      icon: Loader2,
      className: "animate-spin",
    },
    SUCCESS: {
      variant: "default" as const,
      icon: CheckCircle2,
      className: "text-green-500",
    },
    FAILED: {
      variant: "destructive" as const,
      icon: XCircle,
      className: "",
    },
  };

  const { variant, icon: Icon, className } = config[status];

  return (
    <Badge variant={variant} className="flex w-fit items-center gap-1">
      <Icon className={`h-3 w-3 ${className}`} />
      {status}
    </Badge>
  );
}

const columns: Column<ScrapeJob>[] = [
  {
    key: "id",
    label: "Job ID",
    render: (job) => (
      <span className="font-mono text-xs">{job.id.slice(0, 8)}...</span>
    ),
  },
  {
    key: "video_url",
    label: "Video URL",
    render: (job) => (
      <a
        href={job.video_url}
        target="_blank"
        rel="noopener noreferrer"
        className="max-w-[200px] truncate text-sm text-primary hover:underline"
      >
        {job.video_url}
      </a>
    ),
  },
  {
    key: "status",
    label: "Status",
    sortable: true,
    render: (job) => <StatusBadge status={job.status} />,
  },
  {
    key: "comments_scraped",
    label: "Comments",
    sortable: true,
    render: (job) => (
      <span className="font-medium">
        {job.comments_scraped.toLocaleString()}
      </span>
    ),
  },
  {
    key: "started_at",
    label: "Started",
    sortable: true,
    render: (job) => (
      <span className="text-xs text-muted-foreground">
        {new Date(job.started_at).toLocaleString("id-ID")}
      </span>
    ),
  },
  {
    key: "finished_at",
    label: "Finished",
    render: (job) => (
      <span className="text-xs text-muted-foreground">
        {job.finished_at
          ? new Date(job.finished_at).toLocaleString("id-ID")
          : "-"}
      </span>
    ),
  },
];

interface JobTableProps {
  data: ScrapeJob[];
  isLoading: boolean;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSort?: (key: string) => void;
}

export function JobTable({
  data,
  isLoading,
  sortBy,
  sortOrder,
  onSort,
}: JobTableProps) {
  return (
    <DataTable
      columns={columns}
      data={data}
      isLoading={isLoading}
      emptyMessage="Belum ada scraping job."
      sortBy={sortBy}
      sortOrder={sortOrder}
      onSort={onSort}
    />
  );
}
