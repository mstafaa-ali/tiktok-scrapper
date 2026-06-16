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
