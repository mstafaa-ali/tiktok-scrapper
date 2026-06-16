"use client";

import { Video, MessageSquare, ListChecks, TrendingUp } from "lucide-react";
import { StatsCard } from "./stats-card";
import { Skeleton } from "@/components/ui/skeleton";
import { useDashboardStats } from "@/hooks/use-dashboard";

export function StatsGrid() {
  const { data, isLoading, isError } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="rounded-lg border border-destructive/50 p-4 text-destructive">
        Gagal memuat statistik dashboard.
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        title="Total Videos"
        value={data.total_videos}
        icon={Video}
        description="Video yang telah di-scrape"
      />
      <StatsCard
        title="Total Comments"
        value={data.total_comments}
        icon={MessageSquare}
        description="Komentar yang tersimpan"
      />
      <StatsCard
        title="Total Jobs"
        value={data.total_jobs}
        icon={ListChecks}
        description="Scraping jobs yang dijalankan"
      />
      <StatsCard
        title="Success Rate"
        value={`${data.success_rate}%`}
        icon={TrendingUp}
        description="Tingkat keberhasilan scraping"
      />
    </div>
  );
}
