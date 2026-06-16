# Step 7 - Comments Feature

> Panduan untuk membangun fitur Comments: tabel komentar dengan search, filter, dan pagination.

---

## Checklist

- [ ] Buat CommentTable component
- [ ] Buat CommentFilter component
- [ ] Compose Comments Page
- [ ] Implementasi search komentar
- [ ] Implementasi filter berdasarkan video
- [ ] Implementasi pagination

---

## 7.1 CommentTable Component

### Tujuan

Menampilkan daftar komentar dalam tabel dengan kolom: Username, Comment, Likes, Replies.

### File

```typescript
// frontend/src/features/comments/comment-table.tsx
"use client";

import { DataTable, type Column } from "@/components/tables/data-table";
import { Badge } from "@/components/ui/badge";
import type { Comment } from "@/types/comment";

const columns: Column<Comment>[] = [
  {
    key: "username",
    label: "Username",
    sortable: true,
    render: (comment) => (
      <div>
        <span className="font-medium">@{comment.username}</span>
        {comment.nickname && (
          <p className="text-xs text-muted-foreground">{comment.nickname}</p>
        )}
      </div>
    ),
  },
  {
    key: "text",
    label: "Comment",
    render: (comment) => (
      <div className="max-w-[400px]">
        <p className="line-clamp-2 text-sm">{comment.text}</p>
        {comment.is_reply && (
          <Badge variant="outline" className="mt-1 text-xs">
            Reply
          </Badge>
        )}
      </div>
    ),
  },
  {
    key: "likes_count",
    label: "Likes",
    sortable: true,
    render: (comment) => (
      <span className="text-sm">{comment.likes_count.toLocaleString()}</span>
    ),
  },
  {
    key: "reply_count",
    label: "Replies",
    sortable: true,
    render: (comment) => (
      <span className="text-sm">{comment.reply_count.toLocaleString()}</span>
    ),
  },
  {
    key: "created_at",
    label: "Tanggal",
    sortable: true,
    render: (comment) => (
      <span className="text-xs text-muted-foreground">
        {new Date(comment.created_at).toLocaleDateString("id-ID")}
      </span>
    ),
  },
];

interface CommentTableProps {
  data: Comment[];
  isLoading: boolean;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSort?: (key: string) => void;
}

export function CommentTable({
  data,
  isLoading,
  sortBy,
  sortOrder,
  onSort,
}: CommentTableProps) {
  return (
    <DataTable
      columns={columns}
      data={data}
      isLoading={isLoading}
      emptyMessage="Tidak ada komentar ditemukan."
      sortBy={sortBy}
      sortOrder={sortOrder}
      onSort={onSort}
    />
  );
}
```

---

## 7.2 CommentFilter Component

### Tujuan

Menyediakan filter tambahan selain search:

- Filter berdasarkan video (dropdown select)
- Filter reply vs top-level comment

### File

```typescript
// frontend/src/features/comments/comment-filter.tsx
"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useVideos } from "@/hooks/use-videos";

interface CommentFilterProps {
  selectedVideoId: string | undefined;
  onVideoChange: (videoId: string | undefined) => void;
}

export function CommentFilter({
  selectedVideoId,
  onVideoChange,
}: CommentFilterProps) {
  const { data: videosData } = useVideos({ page: 1, page_size: 100 });

  return (
    <div className="flex items-center gap-4">
      <Select
        value={selectedVideoId || "all"}
        onValueChange={(value) =>
          onVideoChange(value === "all" ? undefined : value)
        }
      >
        <SelectTrigger className="w-[250px]">
          <SelectValue placeholder="Semua Video" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Semua Video</SelectItem>
          {videosData?.data.map((video) => (
            <SelectItem key={video.id} value={video.id}>
              <span className="truncate">
                @{video.author_username} - {video.description?.slice(0, 30) || video.url}
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
```

---

## 7.3 Compose Comments Page

### File

```typescript
// frontend/src/app/comments/page.tsx
"use client";

import { useState, useCallback } from "react";
import { CommentTable } from "@/features/comments/comment-table";
import { CommentFilter } from "@/features/comments/comment-filter";
import { SearchInput } from "@/components/tables/search-input";
import { Pagination } from "@/components/tables/pagination";
import { useComments } from "@/hooks/use-comments";

export default function CommentsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [videoId, setVideoId] = useState<string | undefined>();
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const { data, isLoading } = useComments({
    page,
    page_size: 20,
    search: search || undefined,
    video_id: videoId,
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

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
    setPage(1);
  }, []);

  const handleVideoFilter = useCallback((id: string | undefined) => {
    setVideoId(id);
    setPage(1);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Comments</h1>
        <p className="text-muted-foreground">
          Daftar komentar yang telah diambil dari video TikTok.
        </p>
      </div>

      {/* Toolbar: Search & Filter */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <div className="w-full max-w-sm">
          <SearchInput
            placeholder="Cari komentar..."
            onChange={handleSearch}
          />
        </div>
        <CommentFilter
          selectedVideoId={videoId}
          onVideoChange={handleVideoFilter}
        />
      </div>

      {/* Total count */}
      {data && (
        <p className="text-sm text-muted-foreground">
          Menampilkan {data.data.length} dari {data.total.toLocaleString()} komentar
        </p>
      )}

      {/* Table */}
      <CommentTable
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

## 7.4 Alur Kerja Comments Page

```text
1. User membuka halaman Comments
2. Data komentar dimuat dari API (page 1, 20 per page)
3. User bisa melakukan:
   a. Search: ketik keyword → debounce 300ms → fetch ulang
   b. Filter Video: pilih video dari dropdown → fetch ulang
   c. Sort: klik header kolom → toggle asc/desc → fetch ulang
   d. Pagination: klik Sebelumnya/Selanjutnya → fetch page baru
4. Semua perubahan filter/search mereset page ke 1
```

---

## Verifikasi Step 7

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Tabel komentar menampilkan data dengan kolom yang benar
- [ ] Search berfungsi (filter berdasarkan teks komentar)
- [ ] Filter video berfungsi (dropdown berisi daftar video)
- [ ] Sort berfungsi pada kolom yang sortable
- [ ] Pagination berfungsi
- [ ] Badge "Reply" tampil pada komentar yang merupakan reply
- [ ] Total count di atas tabel menampilkan jumlah yang benar
- [ ] Loading state & empty state tampil dengan benar

---

> **Selanjutnya:** Lanjut ke [08-job-monitoring.md](./08-job-monitoring.md)
