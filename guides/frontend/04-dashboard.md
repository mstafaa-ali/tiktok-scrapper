# Step 4 - Dashboard Page

> Panduan untuk membangun halaman Dashboard dengan widget statistik dan recent activity.

---

## Checklist

- [ ] Buat dashboard hook untuk fetch stats
- [ ] Buat StatsCard component
- [ ] Buat RecentActivityList component
- [ ] Compose Dashboard Page
- [ ] Implementasi loading state (skeleton)
- [ ] Implementasi error state

---

## 4.1 Dashboard Hook

### Tujuan

Custom hook untuk mengambil data statistik dashboard dari backend.

### File

```typescript
// frontend/src/hooks/use-dashboard.ts
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/services/api";
import type { DashboardStats, RecentActivity } from "@/types/dashboard";

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: () => apiClient.get<DashboardStats>("/dashboard/stats"),
    refetchInterval: 30 * 1000, // Refetch setiap 30 detik
  });
}

export function useRecentActivity() {
  return useQuery({
    queryKey: ["dashboard", "activity"],
    queryFn: () => apiClient.get<RecentActivity[]>("/dashboard/activity"),
    refetchInterval: 15 * 1000, // Refetch setiap 15 detik
  });
}
```

---

## 4.2 StatsCard Component

### Tujuan

Menampilkan satu metrik statistik (contoh: Total Videos, Total Comments).

### Desain Visual

```text
┌──────────────────┐
│ 📊 Total Videos  │
│                  │
│     1,234        │
│   ▲ +12% today   │
└──────────────────┘
```

### File

```typescript
// frontend/src/features/dashboard/stats-card.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
}

export function StatsCard({ title, value, icon: Icon, description }: StatsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value.toLocaleString()}</div>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## 4.3 StatsGrid Component

### Tujuan

Menampilkan 4 StatsCard dalam grid layout.

### File

```typescript
// frontend/src/features/dashboard/stats-grid.tsx
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
```

---

## 4.4 RecentActivityList Component

### Tujuan

Menampilkan daftar aktivitas terbaru dalam sistem (scraping dimulai, selesai, error, dll.).

### Desain Visual

```text
┌──────────────────────────────────────────┐
│ Recent Activity                          │
├──────────────────────────────────────────┤
│ 🔄 Scraping started for video xyz...     │
│    2 minutes ago                         │
│                                          │
│ ✅ Scraping completed: 1,234 comments    │
│    5 minutes ago                         │
│                                          │
│ ❌ Scraping failed for video abc...      │
│    10 minutes ago                        │
└──────────────────────────────────────────┘
```

### File

```typescript
// frontend/src/features/dashboard/recent-activity.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useRecentActivity } from "@/hooks/use-dashboard";

function getActivityBadge(type: string) {
  switch (type) {
    case "scrape":
      return <Badge variant="secondary">Scrape</Badge>;
    case "video_added":
      return <Badge variant="default">Video</Badge>;
    case "comments_added":
      return <Badge variant="outline">Comments</Badge>;
    default:
      return <Badge>{type}</Badge>;
  }
}

function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const time = new Date(timestamp);
  const diffMs = now.getTime() - time.getTime();
  const diffMin = Math.floor(diffMs / 60000);

  if (diffMin < 1) return "Baru saja";
  if (diffMin < 60) return `${diffMin} menit yang lalu`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours} jam yang lalu`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} hari yang lalu`;
}

export function RecentActivity() {
  const { data, isLoading, isError } = useRecentActivity();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-destructive">
            Gagal memuat aktivitas terbaru.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {data && data.length > 0 ? (
          <div className="space-y-4">
            {data.map((activity) => (
              <div
                key={activity.id}
                className="flex items-start justify-between border-b pb-3 last:border-0"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {getActivityBadge(activity.type)}
                    <span className="text-sm">{activity.description}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {formatTimeAgo(activity.timestamp)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Belum ada aktivitas terbaru.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## 4.5 Compose Dashboard Page

### File

```typescript
// frontend/src/app/page.tsx
import { StatsGrid } from "@/features/dashboard/stats-grid";
import { RecentActivity } from "@/features/dashboard/recent-activity";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Ringkasan sistem scraping TikTok
        </p>
      </div>

      {/* Stats Grid */}
      <StatsGrid />

      {/* Recent Activity */}
      <div className="grid gap-4 lg:grid-cols-2">
        <RecentActivity />
        {/* Area untuk widget tambahan di masa depan */}
      </div>
    </div>
  );
}
```

---

## Verifikasi Step 4

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] StatsCard component ter-render dengan benar
- [ ] StatsGrid menampilkan 4 kartu statistik
- [ ] RecentActivity menampilkan daftar aktivitas
- [ ] Loading state (Skeleton) tampil saat data sedang dimuat
- [ ] Error state tampil jika API gagal
- [ ] Layout responsive (2 kolom di tablet, 4 kolom di desktop untuk stats)

---

> **Selanjutnya:** Lanjut ke [05-scraping.md](./05-scraping.md)
