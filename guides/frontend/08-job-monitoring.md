# Step 8 - Job Monitoring

> Panduan untuk membangun fitur Job Monitoring: tabel status job, filter status, dan auto-refresh.

---

## Checklist

- [ ] Buat JobTable component
- [ ] Buat JobStatusFilter component
- [ ] Compose Jobs Page
- [ ] Implementasi auto-refresh untuk job yang RUNNING
- [ ] Implementasi filter berdasarkan status
- [ ] Implementasi pagination

---

## 8.1 JobTable Component

### Tujuan

Menampilkan daftar scraping jobs dalam tabel dengan kolom: Job ID, Video URL, Status, Comments Scraped, Started, Finished.

### File

```typescript
// frontend/src/features/jobs/job-table.tsx
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
```

---

## 8.2 JobStatusFilter Component

### Tujuan

Menyediakan filter untuk menampilkan job berdasarkan status: All, PENDING, RUNNING, SUCCESS, FAILED.

### File

```typescript
// frontend/src/features/jobs/job-status-filter.tsx
"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { JobStatus } from "@/types/job";

const statuses: { value: JobStatus | "ALL"; label: string }[] = [
  { value: "ALL", label: "Semua" },
  { value: "PENDING", label: "Pending" },
  { value: "RUNNING", label: "Running" },
  { value: "SUCCESS", label: "Success" },
  { value: "FAILED", label: "Failed" },
];

interface JobStatusFilterProps {
  selectedStatus: JobStatus | undefined;
  onStatusChange: (status: JobStatus | undefined) => void;
}

export function JobStatusFilter({
  selectedStatus,
  onStatusChange,
}: JobStatusFilterProps) {
  const activeValue = selectedStatus || "ALL";

  return (
    <div className="flex flex-wrap gap-2">
      {statuses.map((status) => (
        <Button
          key={status.value}
          variant="outline"
          size="sm"
          className={cn(
            activeValue === status.value &&
              "border-primary bg-primary/10 text-primary"
          )}
          onClick={() =>
            onStatusChange(
              status.value === "ALL" ? undefined : (status.value as JobStatus)
            )
          }
        >
          {status.label}
        </Button>
      ))}
    </div>
  );
}
```

---

## 8.3 JobStats Component

### Tujuan

Menampilkan ringkasan statistik job di bagian atas halaman.

### File

```typescript
// frontend/src/features/jobs/job-stats.tsx
"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Clock, Loader2, CheckCircle2, XCircle } from "lucide-react";
import type { ScrapeJob } from "@/types/job";

interface JobStatsProps {
  jobs: ScrapeJob[];
}

export function JobStats({ jobs }: JobStatsProps) {
  const pending = jobs.filter((j) => j.status === "PENDING").length;
  const running = jobs.filter((j) => j.status === "RUNNING").length;
  const success = jobs.filter((j) => j.status === "SUCCESS").length;
  const failed = jobs.filter((j) => j.status === "FAILED").length;

  const stats = [
    {
      label: "Pending",
      value: pending,
      icon: Clock,
      color: "text-muted-foreground",
    },
    {
      label: "Running",
      value: running,
      icon: Loader2,
      color: "text-blue-500",
    },
    {
      label: "Success",
      value: success,
      icon: CheckCircle2,
      color: "text-green-500",
    },
    {
      label: "Failed",
      value: failed,
      icon: XCircle,
      color: "text-destructive",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <CardContent className="flex items-center gap-3 p-4">
            <stat.icon className={`h-5 w-5 ${stat.color}`} />
            <div>
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-xs text-muted-foreground">{stat.label}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

---

## 8.4 Compose Jobs Page

### File

```typescript
// frontend/src/app/jobs/page.tsx
"use client";

import { useState, useCallback } from "react";
import { JobTable } from "@/features/jobs/job-table";
import { JobStatusFilter } from "@/features/jobs/job-status-filter";
import { JobStats } from "@/features/jobs/job-stats";
import { Pagination } from "@/components/tables/pagination";
import { useJobs } from "@/hooks/use-jobs";
import type { JobStatus } from "@/types/job";

export default function JobsPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<JobStatus | undefined>();
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const { data, isLoading } = useJobs({
    page,
    page_size: 15,
    status: statusFilter,
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  const handleSort = useCallback(
    (key: string) => {
      if (sortBy === key) {
        setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
      } else {
        setSortBy(key);
        setSortOrder("desc");
      }
      setPage(1);
    },
    [sortBy]
  );

  const handleStatusChange = useCallback((status: JobStatus | undefined) => {
    setStatusFilter(status);
    setPage(1);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Job Monitoring</h1>
        <p className="text-muted-foreground">
          Pantau status seluruh scraping job.
        </p>
      </div>

      {/* Stats */}
      {data && <JobStats jobs={data.data} />}

      {/* Status Filter */}
      <JobStatusFilter
        selectedStatus={statusFilter}
        onStatusChange={handleStatusChange}
      />

      {/* Table */}
      <JobTable
        data={data?.data ?? []}
        isLoading={isLoading}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSort={handleSort}
      />

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <Pagination
          page={page}
          totalPages={data.total_pages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
```

---

## 8.5 Auto-Refresh untuk Running Jobs

### Tujuan

Ketika ada job yang berstatus `RUNNING`, data jobs secara otomatis di-refetch setiap 5 detik.

### Implementasi di Hook

Update `useJobs` hook agar mendukung auto-refetch:

```typescript
// Update di frontend/src/hooks/use-jobs.ts
export function useJobs(params?: JobListParams) {
  return useQuery({
    queryKey: ["jobs", params],
    queryFn: () => jobService.getAll(params),
    refetchInterval: (query) => {
      // Auto-refetch jika ada job yang masih RUNNING
      const data = query.state.data;
      if (data?.data.some((job) => job.status === "RUNNING")) {
        return 5000;
      }
      return false;
    },
  });
}
```

---

## Verifikasi Step 8

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Tabel jobs menampilkan semua kolom dengan benar
- [ ] Status badge menampilkan icon & warna yang sesuai
- [ ] Filter status berfungsi (klik tombol untuk memfilter)
- [ ] Job stats menampilkan jumlah per status
- [ ] Sort berfungsi pada kolom sortable
- [ ] Pagination berfungsi
- [ ] Auto-refresh berjalan saat ada job RUNNING
- [ ] Auto-refresh berhenti saat tidak ada job RUNNING

---

> **Selanjutnya:** Lanjut ke [09-state-management-ux.md](./09-state-management-ux.md)
