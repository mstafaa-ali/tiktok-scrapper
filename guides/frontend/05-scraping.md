# Step 5 - Scraping Feature

> Panduan untuk membangun fitur scraping: form input URL, validasi, submit ke API, dan tracking progress.

---

## Checklist

- [ ] Buat form schema validasi (Zod)
- [ ] Buat ScrapingForm component
- [ ] Buat ScrapeProgress component
- [ ] Buat ScrapeHistory component (daftar job terbaru)
- [ ] Compose Scraping Page
- [ ] Implementasi real-time polling progress

---

## 5.1 Form Schema Validasi

### Tujuan

Memvalidasi input URL TikTok sebelum dikirim ke backend.

### File

```typescript
// frontend/src/lib/validations/scraping.ts
import { z } from "zod";

export const scrapingFormSchema = z.object({
  videoUrl: z
    .string()
    .min(1, "URL video wajib diisi")
    .url("Format URL tidak valid")
    .refine(
      (url) => {
        // Menerima berbagai format URL TikTok
        return (
          url.includes("tiktok.com") ||
          url.includes("vm.tiktok.com") ||
          url.includes("vt.tiktok.com")
        );
      },
      "URL harus dari TikTok (tiktok.com)"
    ),
});

export type ScrapingFormValues = z.infer<typeof scrapingFormSchema>;
```

---

## 5.2 ScrapingForm Component

### Tujuan

Form untuk memasukkan URL video TikTok dan memulai proses scraping.

### Desain Visual

```text
┌────────────────────────────────────────────────┐
│  Scrape Video Comments                         │
│                                                │
│  Video URL                                     │
│  ┌──────────────────────────────────────────┐  │
│  │ https://www.tiktok.com/@user/video/123   │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  [🔄 Start Scraping]                           │
│                                                │
└────────────────────────────────────────────────┘
```

### File

```typescript
// frontend/src/features/scraping/scraping-form.tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, Loader2 } from "lucide-react";
import { useScraping } from "@/hooks/use-scraping";
import {
  scrapingFormSchema,
  type ScrapingFormValues,
} from "@/lib/validations/scraping";

interface ScrapingFormProps {
  onSuccess?: (jobId: string) => void;
}

export function ScrapingForm({ onSuccess }: ScrapingFormProps) {
  const scraping = useScraping();

  const form = useForm<ScrapingFormValues>({
    resolver: zodResolver(scrapingFormSchema),
    defaultValues: {
      videoUrl: "",
    },
  });

  async function onSubmit(values: ScrapingFormValues) {
    try {
      const result = await scraping.mutateAsync({
        video_url: values.videoUrl,
      });
      form.reset();
      onSuccess?.(result.job_id);
    } catch (error) {
      // Error ditangani oleh TanStack Query
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Download className="h-5 w-5" />
          Scrape Video Comments
        </CardTitle>
        <CardDescription>
          Masukkan URL video TikTok untuk memulai scraping komentar.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="videoUrl" className="text-sm font-medium">
              Video URL
            </label>
            <Input
              id="videoUrl"
              placeholder="https://www.tiktok.com/@username/video/1234567890"
              {...form.register("videoUrl")}
              disabled={scraping.isPending}
            />
            {form.formState.errors.videoUrl && (
              <p className="text-sm text-destructive">
                {form.formState.errors.videoUrl.message}
              </p>
            )}
          </div>

          {/* Error dari API */}
          {scraping.isError && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              Gagal memulai scraping. Silakan coba lagi.
            </div>
          )}

          {/* Success message */}
          {scraping.isSuccess && (
            <div className="rounded-md bg-green-50 p-3 text-sm text-green-700 dark:bg-green-950 dark:text-green-300">
              Scraping berhasil dimulai! Job ID: {scraping.data.job_id}
            </div>
          )}

          <Button type="submit" disabled={scraping.isPending} className="w-full">
            {scraping.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Memulai Scraping...
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Start Scraping
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
```

---

## 5.3 ScrapeProgress Component

### Tujuan

Menampilkan progress dari scraping job yang sedang berjalan. Melakukan polling otomatis ke API setiap 5 detik selama job masih berstatus `RUNNING`.

### Desain Visual

```text
┌────────────────────────────────────────────────┐
│  Job Progress                                  │
│                                                │
│  Status: 🔄 RUNNING                            │
│  Comments scraped: 342                          │
│  Started: 2 minutes ago                         │
│                                                │
│  ████████████░░░░░░░░ (auto-polling)            │
└────────────────────────────────────────────────┘
```

### File

```typescript
// frontend/src/features/scraping/scrape-progress.tsx
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
```

---

## 5.4 ScrapeHistory Component

### Tujuan

Menampilkan daftar job scraping terbaru (5 terakhir) agar user bisa melihat riwayat tanpa berpindah ke halaman Jobs.

### File

```typescript
// frontend/src/features/scraping/scrape-history.tsx
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
```

---

## 5.5 Compose Scraping Page

### File

```typescript
// frontend/src/app/scraping/page.tsx
"use client";

import { useState } from "react";
import { ScrapingForm } from "@/features/scraping/scraping-form";
import { ScrapeProgress } from "@/features/scraping/scrape-progress";
import { ScrapeHistory } from "@/features/scraping/scrape-history";

export default function ScrapingPage() {
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Scraping</h1>
        <p className="text-muted-foreground">
          Masukkan URL video TikTok untuk mengambil komentar.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Form */}
        <div className="space-y-4">
          <ScrapingForm onSuccess={(jobId) => setActiveJobId(jobId)} />

          {/* Progress */}
          {activeJobId && <ScrapeProgress jobId={activeJobId} />}
        </div>

        {/* History */}
        <ScrapeHistory />
      </div>
    </div>
  );
}
```

---

## 5.6 Alur Kerja Scraping

```text
1. User memasukkan URL video TikTok
2. Form divalidasi oleh Zod
3. Submit dikirim ke POST /videos/scrape
4. Backend mengembalikan job_id
5. ScrapeProgress mulai polling GET /jobs/:id setiap 5 detik
6. Saat status berubah (SUCCESS/FAILED), polling berhenti
7. ScrapeHistory diperbarui otomatis
```

---

## Verifikasi Step 5

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Form validasi URL TikTok berfungsi (tolak URL non-TikTok)
- [ ] Submit form memanggil API dengan benar
- [ ] Progress card tampil setelah submit
- [ ] Auto-polling berjalan saat status RUNNING
- [ ] Auto-polling berhenti saat status SUCCESS/FAILED
- [ ] Error message tampil jika scraping gagal
- [ ] Riwayat scraping menampilkan job terbaru

---

> **Selanjutnya:** Lanjut ke [06-videos.md](./06-videos.md)
