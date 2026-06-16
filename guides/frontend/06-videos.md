# Step 6 - Videos Feature

> Panduan untuk membangun fitur Video List dan Video Detail page.

---

## Checklist

- [ ] Buat DataTable component (reusable)
- [ ] Buat VideoTable component
- [ ] Buat SearchInput component
- [ ] Compose Videos List Page
- [ ] Buat VideoDetail component
- [ ] Compose Video Detail Page
- [ ] Implementasi pagination
- [ ] Implementasi search & sort

---

## 6.1 DataTable Component (Reusable)

### Tujuan

Komponen tabel generik yang bisa digunakan ulang oleh Videos, Comments, dan Jobs page.

### File

```typescript
// frontend/src/components/tables/data-table.tsx
"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";

export interface Column<T> {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  emptyMessage?: string;
  onSort?: (key: string) => void;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  isLoading,
  emptyMessage = "Tidak ada data.",
  onSort,
  sortBy,
  sortOrder,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead
                key={column.key}
                className={column.sortable ? "cursor-pointer select-none" : ""}
                onClick={() => column.sortable && onSort?.(column.key)}
              >
                <div className="flex items-center gap-1">
                  {column.label}
                  {column.sortable && sortBy === column.key && (
                    <span className="text-xs">
                      {sortOrder === "asc" ? "↑" : "↓"}
                    </span>
                  )}
                </div>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={columns.length}
                className="h-24 text-center text-muted-foreground"
              >
                {emptyMessage}
              </TableCell>
            </TableRow>
          ) : (
            data.map((item, index) => (
              <TableRow key={index}>
                {columns.map((column) => (
                  <TableCell key={column.key}>
                    {column.render
                      ? column.render(item)
                      : String(item[column.key] ?? "")}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
```

---

## 6.2 Pagination Component

### File

```typescript
// frontend/src/components/tables/pagination.tsx
"use client";

import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
  return (
    <div className="flex items-center justify-between py-4">
      <p className="text-sm text-muted-foreground">
        Halaman {page} dari {totalPages}
      </p>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
        >
          <ChevronLeft className="h-4 w-4" />
          Sebelumnya
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
        >
          Selanjutnya
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
```

---

## 6.3 SearchInput Component

### File

```typescript
// frontend/src/components/tables/search-input.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { useEffect, useState } from "react";

interface SearchInputProps {
  placeholder?: string;
  value?: string;
  onChange: (value: string) => void;
  debounceMs?: number;
}

export function SearchInput({
  placeholder = "Cari...",
  value: externalValue = "",
  onChange,
  debounceMs = 300,
}: SearchInputProps) {
  const [internalValue, setInternalValue] = useState(externalValue);

  useEffect(() => {
    const timer = setTimeout(() => {
      onChange(internalValue);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [internalValue, debounceMs, onChange]);

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        placeholder={placeholder}
        value={internalValue}
        onChange={(e) => setInternalValue(e.target.value)}
        className="pl-10"
      />
    </div>
  );
}
```

---

## 6.4 VideoTable Component

### Tujuan

Menampilkan daftar video dalam tabel dengan kolom: Video (URL/description), Author, Comments, Last Scrape.

### File

```typescript
// frontend/src/features/videos/video-table.tsx
"use client";

import Link from "next/link";
import { DataTable, type Column } from "@/components/tables/data-table";
import type { Video } from "@/types/video";

const columns: Column<Video>[] = [
  {
    key: "description",
    label: "Video",
    sortable: true,
    render: (video) => (
      <Link
        href={`/videos/${video.id}`}
        className="text-primary hover:underline"
      >
        <span className="line-clamp-1 max-w-[300px]">
          {video.description || video.url}
        </span>
      </Link>
    ),
  },
  {
    key: "author_username",
    label: "Author",
    sortable: true,
    render: (video) => (
      <span className="text-sm">@{video.author_username}</span>
    ),
  },
  {
    key: "comment_count",
    label: "Comments",
    sortable: true,
    render: (video) => (
      <span className="font-medium">{video.comment_count.toLocaleString()}</span>
    ),
  },
  {
    key: "updated_at",
    label: "Last Scrape",
    sortable: true,
    render: (video) => (
      <span className="text-sm text-muted-foreground">
        {new Date(video.updated_at).toLocaleDateString("id-ID")}
      </span>
    ),
  },
];

interface VideoTableProps {
  data: Video[];
  isLoading: boolean;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSort?: (key: string) => void;
}

export function VideoTable({
  data,
  isLoading,
  sortBy,
  sortOrder,
  onSort,
}: VideoTableProps) {
  return (
    <DataTable
      columns={columns}
      data={data}
      isLoading={isLoading}
      emptyMessage="Belum ada video yang di-scrape."
      sortBy={sortBy}
      sortOrder={sortOrder}
      onSort={onSort}
    />
  );
}
```

---

## 6.5 Compose Videos List Page

### File

```typescript
// frontend/src/app/videos/page.tsx
"use client";

import { useState, useCallback } from "react";
import { VideoTable } from "@/features/videos/video-table";
import { SearchInput } from "@/components/tables/search-input";
import { Pagination } from "@/components/tables/pagination";
import { useVideos } from "@/hooks/use-videos";

export default function VideosPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const { data, isLoading } = useVideos({
    page,
    page_size: 10,
    search: search || undefined,
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
      setPage(1); // Reset ke halaman pertama saat sort berubah
    },
    [sortBy]
  );

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
    setPage(1); // Reset ke halaman pertama saat search berubah
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Videos</h1>
        <p className="text-muted-foreground">
          Daftar video TikTok yang telah di-scrape.
        </p>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="w-full max-w-sm">
          <SearchInput
            placeholder="Cari video..."
            onChange={handleSearch}
          />
        </div>
      </div>

      {/* Table */}
      <VideoTable
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

## 6.6 VideoDetail Component

### Tujuan

Menampilkan detail lengkap satu video: metadata, statistik, riwayat scraping, dan preview komentar.

### Desain Visual

```text
┌─────────────────────────────────────────────────┐
│  ← Back to Videos                               │
│                                                 │
│  Video Information                              │
│  ┌───────────────────────────────────────┐      │
│  │ Author: @username                     │      │
│  │ Description: Lorem ipsum dolor sit... │      │
│  │ Views: 1,234,567                      │      │
│  │ Likes: 123,456                        │      │
│  │ Comments: 1,234                       │      │
│  │ Shares: 567                           │      │
│  └───────────────────────────────────────┘      │
│                                                 │
│  Scraping History                               │
│  ┌───────────────────────────────────────┐      │
│  │ Job ID | Status | Comments | Date     │      │
│  │ ...    | ...    | ...      | ...      │      │
│  └───────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```

### File

```typescript
// frontend/src/features/videos/video-detail.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ExternalLink } from "lucide-react";
import Link from "next/link";
import { useVideo } from "@/hooks/use-videos";

interface VideoDetailProps {
  videoId: string;
}

export function VideoDetail({ videoId }: VideoDetailProps) {
  const { data: video, isLoading, isError } = useVideo(videoId);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (isError || !video) {
    return (
      <div className="space-y-4">
        <Link href="/videos">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Kembali ke Videos
          </Button>
        </Link>
        <p className="text-destructive">Video tidak ditemukan.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link href="/videos">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Kembali ke Videos
        </Button>
      </Link>

      {/* Video Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Video Information
            <a
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              <ExternalLink className="inline h-4 w-4" /> Buka di TikTok
            </a>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-3">
              <div>
                <span className="text-sm text-muted-foreground">Author</span>
                <p className="font-medium">
                  @{video.author_username}
                  {video.author_nickname && (
                    <span className="text-muted-foreground">
                      {" "}
                      ({video.author_nickname})
                    </span>
                  )}
                </p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">
                  Description
                </span>
                <p className="text-sm">{video.description || "-"}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">TikTok ID</span>
                <p className="font-mono text-xs">{video.tiktok_id}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg border p-3 text-center">
                <p className="text-2xl font-bold">
                  {video.view_count.toLocaleString()}
                </p>
                <p className="text-xs text-muted-foreground">Views</p>
              </div>
              <div className="rounded-lg border p-3 text-center">
                <p className="text-2xl font-bold">
                  {video.like_count.toLocaleString()}
                </p>
                <p className="text-xs text-muted-foreground">Likes</p>
              </div>
              <div className="rounded-lg border p-3 text-center">
                <p className="text-2xl font-bold">
                  {video.comment_count.toLocaleString()}
                </p>
                <p className="text-xs text-muted-foreground">Comments</p>
              </div>
              <div className="rounded-lg border p-3 text-center">
                <p className="text-2xl font-bold">
                  {video.share_count.toLocaleString()}
                </p>
                <p className="text-xs text-muted-foreground">Shares</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Timestamps */}
      <Card>
        <CardContent className="flex gap-6 p-4">
          <div>
            <span className="text-xs text-muted-foreground">Ditambahkan</span>
            <p className="text-sm">
              {new Date(video.created_at).toLocaleString("id-ID")}
            </p>
          </div>
          <div>
            <span className="text-xs text-muted-foreground">
              Terakhir diperbarui
            </span>
            <p className="text-sm">
              {new Date(video.updated_at).toLocaleString("id-ID")}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 6.7 Compose Video Detail Page

### File

```typescript
// frontend/src/app/videos/[id]/page.tsx
import { VideoDetail } from "@/features/videos/video-detail";

export default function VideoDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return <VideoDetail videoId={params.id} />;
}
```

---

## Verifikasi Step 6

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] DataTable component bisa digunakan ulang dengan column config berbeda
- [ ] Video list menampilkan data dalam tabel
- [ ] Pagination berfungsi (navigasi halaman)
- [ ] Search berfungsi (filter berdasarkan keyword)
- [ ] Sort berfungsi (klik header kolom)
- [ ] Klik video membuka halaman detail
- [ ] Video detail menampilkan metadata lengkap
- [ ] Loading state (skeleton) tampil
- [ ] Empty state tampil saat tidak ada data

---

> **Selanjutnya:** Lanjut ke [07-comments.md](./07-comments.md)
