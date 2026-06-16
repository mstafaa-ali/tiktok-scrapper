# Step 10 - Error Handling & Optimization

> Panduan untuk implementasi error handling yang konsisten, loading states, empty states, dan optimasi performa aplikasi.

---

## Checklist

- [ ] Buat Error Boundary component
- [ ] Buat komponen loading state (skeleton patterns)
- [ ] Buat komponen empty state
- [ ] Buat komponen error state
- [ ] Implementasi error handling global
- [ ] Optimasi performa (React.memo, lazy loading)
- [ ] Implementasi SEO metadata per halaman
- [ ] Final review & testing

---

## 10.1 Error Boundary

### Tujuan

Menangkap error yang terjadi di React component tree agar tidak crash seluruh aplikasi.

### File

```typescript
// frontend/src/components/ui/error-boundary.tsx
"use client";

import { Component, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center gap-4 p-8 text-center">
          <AlertTriangle className="h-12 w-12 text-destructive" />
          <div>
            <h2 className="text-lg font-semibold">Terjadi Kesalahan</h2>
            <p className="text-sm text-muted-foreground">
              {this.state.error?.message || "Sesuatu yang tidak terduga terjadi."}
            </p>
          </div>
          <Button
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Coba Lagi
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Integrasikan ke Layout

```typescript
// Update frontend/src/app/layout.tsx
import { ErrorBoundary } from "@/components/ui/error-boundary";

// Bungkus MainLayout children
<MainLayout>
  <ErrorBoundary>{children}</ErrorBoundary>
</MainLayout>
```

---

## 10.2 Loading State Patterns

### Tujuan

Konsistensi tampilan loading di seluruh aplikasi menggunakan skeleton patterns.

### Page Loading Skeleton

```typescript
// frontend/src/components/ui/page-skeleton.tsx
import { Skeleton } from "@/components/ui/skeleton";

export function PageSkeleton() {
  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>

      {/* Content */}
      <div className="space-y-4">
        <Skeleton className="h-10 w-full max-w-sm" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-10 w-64" />
      </div>
    </div>
  );
}
```

### Table Loading Skeleton

```typescript
// frontend/src/components/ui/table-skeleton.tsx
import { Skeleton } from "@/components/ui/skeleton";

interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

export function TableSkeleton({ rows = 5, columns = 4 }: TableSkeletonProps) {
  return (
    <div className="rounded-md border">
      {/* Header */}
      <div className="flex gap-4 border-b p-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 border-b p-4 last:border-0">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}
```

---

## 10.3 Empty State Component

### File

```typescript
// frontend/src/components/ui/empty-state.tsx
import { type LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-dashed p-12 text-center">
      <Icon className="h-12 w-12 text-muted-foreground/50" />
      <div>
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      {actionLabel && onAction && (
        <Button onClick={onAction}>{actionLabel}</Button>
      )}
    </div>
  );
}
```

### Contoh Penggunaan

```typescript
// Di Videos page, jika tidak ada data
<EmptyState
  icon={Video}
  title="Belum ada video"
  description="Mulai scraping video TikTok untuk melihat data di sini."
  actionLabel="Mulai Scraping"
  onAction={() => router.push("/scraping")}
/>
```

---

## 10.4 Error State Component

### File

```typescript
// frontend/src/components/ui/error-state.tsx
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Terjadi Kesalahan",
  message = "Gagal memuat data. Silakan coba lagi.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-destructive/30 bg-destructive/5 p-8 text-center">
      <AlertTriangle className="h-10 w-10 text-destructive" />
      <div>
        <h3 className="font-semibold text-destructive">{title}</h3>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Coba Lagi
        </Button>
      )}
    </div>
  );
}
```

---

## 10.5 Global Error Handling (API)

### Tujuan

Menangani error API secara terpusat di TanStack Query config.

### Update QueryClient Config

```typescript
// Update frontend/src/lib/query-provider.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: (failureCount, error) => {
        // Jangan retry untuk error 4xx
        if (error && typeof error === "object" && "status" in error) {
          const status = (error as { status: number }).status;
          if (status >= 400 && status < 500) return false;
        }
        return failureCount < 2;
      },
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});
```

---

## 10.6 Optimasi Performa

### React.memo untuk Komponen Berat

Gunakan `React.memo` pada komponen yang sering re-render tapi data jarang berubah:

```typescript
// Contoh: StatsCard
export const StatsCard = React.memo(function StatsCard({
  title,
  value,
  icon: Icon,
  description,
}: StatsCardProps) {
  // ... component code
});
```

### Dynamic Import (Lazy Loading)

Gunakan `next/dynamic` untuk komponen berat yang tidak perlu dimuat langsung:

```typescript
// Contoh: Chart component di dashboard
import dynamic from "next/dynamic";

const Chart = dynamic(() => import("@/components/charts/activity-chart"), {
  loading: () => <Skeleton className="h-64" />,
  ssr: false,
});
```

### Image Optimization

Gunakan `next/image` untuk semua gambar:

```typescript
import Image from "next/image";

<Image
  src="/logo.png"
  alt="TikTok Scraper"
  width={32}
  height={32}
  priority
/>
```

---

## 10.7 SEO Metadata per Halaman

### Tujuan

Setiap halaman memiliki metadata SEO yang sesuai.

### Contoh per Page

```typescript
// frontend/src/app/page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard | TikTok Scraper",
  description: "Ringkasan statistik scraping komentar video TikTok",
};

// frontend/src/app/videos/page.tsx
export const metadata: Metadata = {
  title: "Videos | TikTok Scraper",
  description: "Daftar video TikTok yang telah di-scrape",
};

// frontend/src/app/comments/page.tsx
export const metadata: Metadata = {
  title: "Comments | TikTok Scraper",
  description: "Daftar komentar dari video TikTok",
};

// frontend/src/app/scraping/page.tsx
export const metadata: Metadata = {
  title: "Scraping | TikTok Scraper",
  description: "Mulai scraping komentar dari video TikTok",
};

// frontend/src/app/jobs/page.tsx
export const metadata: Metadata = {
  title: "Job Monitoring | TikTok Scraper",
  description: "Pantau status scraping jobs",
};
```

> **Catatan:** Metadata export hanya bisa digunakan di Server Components. Jika page adalah Client Component (`"use client"`), pindahkan metadata ke `layout.tsx` atau gunakan file `metadata.ts` terpisah.

---

## 10.8 Final Review Checklist

### Fungsionalitas

- [ ] Semua halaman bisa diakses dan menampilkan data
- [ ] Navigasi sidebar berfungsi di desktop dan mobile
- [ ] Scraping form berfungsi end-to-end
- [ ] Pagination, search, sort berfungsi di semua tabel
- [ ] Dark mode berfungsi dan persist
- [ ] Toast notifications tampil di aksi penting

### Error Handling

- [ ] Loading state (skeleton) tampil di semua halaman saat data dimuat
- [ ] Empty state tampil saat tidak ada data
- [ ] Error state tampil saat API gagal
- [ ] Error boundary menangkap crash React

### UX

- [ ] Responsif di mobile, tablet, dan desktop
- [ ] Animasi transisi halus
- [ ] Breadcrumbs di halaman detail
- [ ] Debounce pada search input

### Performa

- [ ] Build berhasil tanpa error (`npm run build`)
- [ ] Tidak ada console errors di browser
- [ ] Lighthouse score reasonable (Performance > 80)

---

> **Selesai!** Frontend development guide telah selesai. Kembali ke [00-overview.md](./00-overview.md) untuk melihat gambaran keseluruhan.
