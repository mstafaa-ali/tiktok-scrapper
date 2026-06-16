"use client";

import { useState, useCallback } from "react";
import { VideoTable } from "@/features/videos/video-table";
import { SearchInput } from "@/components/tables/search-input";
import { Pagination } from "@/components/tables/pagination";
import { useVideos } from "@/hooks/use-videos";

import { useFilterStore } from "@/stores/filter-store";

export function VideosClient() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const videosPageSize = useFilterStore((state) => state.videosPageSize);

  const { data, isLoading } = useVideos({
    page,
    page_size: videosPageSize,
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
        data={(Array.isArray(data) ? data : data?.data) ?? []}
        isLoading={isLoading}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSort={handleSort}
      />

      {/* Pagination */}
      {data && "total_pages" in data && (data as import("@/types/video").VideoListResponse).total_pages > 1 && (
        <Pagination
          page={page}
          totalPages={(data as import("@/types/video").VideoListResponse).total_pages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
