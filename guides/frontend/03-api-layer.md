# Step 3 - API Layer & Data Fetching

> Panduan untuk membangun service layer, API client, TypeScript types, dan custom hooks menggunakan TanStack Query.

---

## Checklist

- [ ] Setup base API client
- [ ] Definisikan TypeScript types
- [ ] Buat video service
- [ ] Buat comment service
- [ ] Buat job service
- [ ] Buat scraping service
- [ ] Buat custom hooks dengan TanStack Query

---

## 3.1 Base API Client

### Tujuan

Satu instance API client yang digunakan oleh semua service. Menangani base URL, headers, dan error handling secara terpusat.

### File

```typescript
// frontend/src/services/api.ts

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiError {
  message: string;
  status: number;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = {
      message: `API Error: ${response.statusText}`,
      status: response.status,
    };

    // Coba parse error body dari backend
    try {
      const body = await response.json();
      error.message = body.detail || body.message || error.message;
    } catch {
      // Gunakan default error message
    }

    throw error;
  }

  return response.json();
}

export const apiClient = {
  get: async <T>(endpoint: string, params?: Record<string, string>): Promise<T> => {
    const url = new URL(`${API_BASE_URL}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) url.searchParams.append(key, value);
      });
    }

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    return handleResponse<T>(response);
  },

  post: async <T>(endpoint: string, body?: unknown): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    return handleResponse<T>(response);
  },
};
```

---

## 3.2 TypeScript Types

### Tujuan

Definisikan semua tipe data yang sesuai dengan response dari backend API.

### Video Types

```typescript
// frontend/src/types/video.ts

export interface Video {
  id: string;
  tiktok_id: string;
  url: string;
  author_username: string;
  author_nickname: string;
  description: string;
  comment_count: number;
  like_count: number;
  share_count: number;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface VideoListResponse {
  data: Video[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface VideoListParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}
```

### Comment Types

```typescript
// frontend/src/types/comment.ts

export interface Comment {
  id: string;
  video_id: string;
  tiktok_comment_id: string;
  text: string;
  username: string;
  nickname: string;
  likes_count: number;
  reply_count: number;
  is_reply: boolean;
  parent_comment_id: string | null;
  created_at: string;
}

export interface CommentListResponse {
  data: Comment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CommentListParams {
  page?: number;
  page_size?: number;
  search?: string;
  video_id?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}
```

### Job Types

```typescript
// frontend/src/types/job.ts

export type JobStatus = "PENDING" | "RUNNING" | "SUCCESS" | "FAILED";

export interface ScrapeJob {
  id: string;
  video_id: string;
  video_url: string;
  status: JobStatus;
  comments_scraped: number;
  error_message: string | null;
  started_at: string;
  finished_at: string | null;
  created_at: string;
}

export interface JobListResponse {
  data: ScrapeJob[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface JobListParams {
  page?: number;
  page_size?: number;
  status?: JobStatus;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}
```

### Dashboard Types

```typescript
// frontend/src/types/dashboard.ts

export interface DashboardStats {
  total_videos: number;
  total_comments: number;
  total_jobs: number;
  success_rate: number;
}

export interface RecentActivity {
  id: string;
  type: "scrape" | "video_added" | "comments_added";
  description: string;
  timestamp: string;
}
```

### Scraping Types

```typescript
// frontend/src/types/scraping.ts

export interface ScrapeRequest {
  video_url: string;
}

export interface ScrapeResponse {
  job_id: string;
  status: string;
  message: string;
}
```

---

## 3.3 Video Service

### File

```typescript
// frontend/src/services/videos.ts
import { apiClient } from "./api";
import type { Video, VideoListResponse, VideoListParams } from "@/types/video";

export const videoService = {
  getAll: async (params?: VideoListParams): Promise<VideoListResponse> => {
    const queryParams: Record<string, string> = {};
    if (params?.page) queryParams.page = String(params.page);
    if (params?.page_size) queryParams.page_size = String(params.page_size);
    if (params?.search) queryParams.search = params.search;
    if (params?.sort_by) queryParams.sort_by = params.sort_by;
    if (params?.sort_order) queryParams.sort_order = params.sort_order;

    return apiClient.get<VideoListResponse>("/videos", queryParams);
  },

  getById: async (id: string): Promise<Video> => {
    return apiClient.get<Video>(`/videos/${id}`);
  },
};
```

---

## 3.4 Comment Service

### File

```typescript
// frontend/src/services/comments.ts
import { apiClient } from "./api";
import type { CommentListResponse, CommentListParams } from "@/types/comment";

export const commentService = {
  getAll: async (params?: CommentListParams): Promise<CommentListResponse> => {
    const queryParams: Record<string, string> = {};
    if (params?.page) queryParams.page = String(params.page);
    if (params?.page_size) queryParams.page_size = String(params.page_size);
    if (params?.search) queryParams.search = params.search;
    if (params?.video_id) queryParams.video_id = params.video_id;
    if (params?.sort_by) queryParams.sort_by = params.sort_by;
    if (params?.sort_order) queryParams.sort_order = params.sort_order;

    return apiClient.get<CommentListResponse>("/comments", queryParams);
  },

  search: async (query: string): Promise<CommentListResponse> => {
    return apiClient.get<CommentListResponse>("/comments/search", { q: query });
  },
};
```

---

## 3.5 Job Service

### File

```typescript
// frontend/src/services/jobs.ts
import { apiClient } from "./api";
import type { ScrapeJob, JobListResponse, JobListParams } from "@/types/job";

export const jobService = {
  getAll: async (params?: JobListParams): Promise<JobListResponse> => {
    const queryParams: Record<string, string> = {};
    if (params?.page) queryParams.page = String(params.page);
    if (params?.page_size) queryParams.page_size = String(params.page_size);
    if (params?.status) queryParams.status = params.status;
    if (params?.sort_by) queryParams.sort_by = params.sort_by;
    if (params?.sort_order) queryParams.sort_order = params.sort_order;

    return apiClient.get<JobListResponse>("/jobs", queryParams);
  },

  getById: async (id: string): Promise<ScrapeJob> => {
    return apiClient.get<ScrapeJob>(`/jobs/${id}`);
  },
};
```

---

## 3.6 Scraping Service

### File

```typescript
// frontend/src/services/scraping.ts
import { apiClient } from "./api";
import type { ScrapeRequest, ScrapeResponse } from "@/types/scraping";

export const scrapingService = {
  startScraping: async (data: ScrapeRequest): Promise<ScrapeResponse> => {
    return apiClient.post<ScrapeResponse>("/videos/scrape", data);
  },
};
```

---

## 3.7 Custom Hooks (TanStack Query)

### Tujuan

Membungkus service calls dengan TanStack Query untuk mendapatkan caching, loading state, error handling, dan auto-refetch secara otomatis.

### useVideos

```typescript
// frontend/src/hooks/use-videos.ts
import { useQuery } from "@tanstack/react-query";
import { videoService } from "@/services/videos";
import type { VideoListParams } from "@/types/video";

export function useVideos(params?: VideoListParams) {
  return useQuery({
    queryKey: ["videos", params],
    queryFn: () => videoService.getAll(params),
  });
}

export function useVideo(id: string) {
  return useQuery({
    queryKey: ["video", id],
    queryFn: () => videoService.getById(id),
    enabled: !!id,
  });
}
```

### useComments

```typescript
// frontend/src/hooks/use-comments.ts
import { useQuery } from "@tanstack/react-query";
import { commentService } from "@/services/comments";
import type { CommentListParams } from "@/types/comment";

export function useComments(params?: CommentListParams) {
  return useQuery({
    queryKey: ["comments", params],
    queryFn: () => commentService.getAll(params),
  });
}
```

### useJobs

```typescript
// frontend/src/hooks/use-jobs.ts
import { useQuery } from "@tanstack/react-query";
import { jobService } from "@/services/jobs";
import type { JobListParams } from "@/types/job";

export function useJobs(params?: JobListParams) {
  return useQuery({
    queryKey: ["jobs", params],
    queryFn: () => jobService.getAll(params),
  });
}

export function useJob(id: string) {
  return useQuery({
    queryKey: ["job", id],
    queryFn: () => jobService.getById(id),
    enabled: !!id,
    refetchInterval: (query) => {
      // Auto-refetch setiap 5 detik jika status masih RUNNING
      const data = query.state.data;
      if (data && data.status === "RUNNING") return 5000;
      return false;
    },
  });
}
```

### useScraping

```typescript
// frontend/src/hooks/use-scraping.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { scrapingService } from "@/services/scraping";
import type { ScrapeRequest } from "@/types/scraping";

export function useScraping() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ScrapeRequest) => scrapingService.startScraping(data),
    onSuccess: () => {
      // Invalidate jobs & videos queries setelah scraping berhasil dimulai
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["videos"] });
    },
  });
}
```

---

## Verifikasi Step 3

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] File `src/services/api.ts` sudah dibuat dan terkonfigurasi
- [ ] Semua type files ada di `src/types/`
- [ ] Semua service files ada di `src/services/`
- [ ] Semua custom hooks ada di `src/hooks/`
- [ ] Project masih bisa build tanpa error (`npm run build`)

---

> **Selanjutnya:** Lanjut ke [04-dashboard.md](./04-dashboard.md)
