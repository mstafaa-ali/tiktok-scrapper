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
