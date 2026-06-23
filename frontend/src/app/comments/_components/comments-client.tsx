"use client";

import { useState, useCallback, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { CommentTable } from "@/features/comments/comment-table";
import { CommentFilter } from "@/features/comments/comment-filter";
import { SearchInput } from "@/components/tables/search-input";
import { Pagination } from "@/components/tables/pagination";
import { useComments } from "@/hooks/use-comments";
import { commentService } from "@/services/comments";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { useFilterStore } from "@/stores/filter-store";

export function CommentsClient() {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [videoId, setVideoId] = useState<string | undefined>(searchParams.get("videoId") || undefined);
  const [sortBy, setSortBy] = useState("scraped_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const commentsPageSize = useFilterStore((state) => state.commentsPageSize);

  // Jika URL berubah
  useEffect(() => {
    const vid = searchParams.get("videoId");
    if (vid) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setVideoId(vid);
    }
  }, [searchParams]);

  const { data, isLoading } = useComments({
    page,
    page_size: commentsPageSize,
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
    if (!id) {
        router.push("/comments");
    } else {
        router.push(`/comments?videoId=${id}`);
    }
  }, [router]);

  const handleExport = useCallback((format: string) => {
    const url = commentService.getExportUrl(videoId, format);
    window.open(url, "_blank");
  }, [videoId]);

  const commentsList = Array.isArray(data) ? data : data?.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Comments</h1>
        <p className="text-muted-foreground">
          Daftar komentar yang telah diambil dari video TikTok.
        </p>
      </div>

      {/* Toolbar: Search & Filter */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
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
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => handleExport("csv")}>
              Export as CSV
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleExport("excel")}>
              Export as Excel
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Total count */}
      {data && Array.isArray(data) && (
        <p className="text-sm text-muted-foreground">
          Menampilkan {data.length} komentar
        </p>
      )}

      {/* Table */}
      <CommentTable
        data={commentsList}
        isLoading={isLoading}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSort={handleSort}
      />

      {/* Pagination */}
      {data && "total_pages" in data && (data as import("@/types/comment").CommentListResponse).total_pages > 1 && (
        <Pagination
          page={page}
          totalPages={(data as import("@/types/comment").CommentListResponse).total_pages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
