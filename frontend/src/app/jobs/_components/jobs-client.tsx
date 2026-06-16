"use client";

import { useState, useCallback } from "react";
import { JobTable } from "@/features/jobs/job-table";
import { JobStatusFilter } from "@/features/jobs/job-status-filter";
import { JobStats } from "@/features/jobs/job-stats";
import { Pagination } from "@/components/tables/pagination";
import { useJobs } from "@/hooks/use-jobs";
import type { JobStatus } from "@/types/job";

import { useFilterStore } from "@/stores/filter-store";

export function JobsClient() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<JobStatus | undefined>();
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const jobsPageSize = useFilterStore((state) => state.jobsPageSize);

  const { data, isLoading } = useJobs({
    page,
    page_size: jobsPageSize,
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
