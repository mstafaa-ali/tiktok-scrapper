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
        href={`/comments?videoId=${video.id}`}
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
      <span className="font-medium">{(video.comment_count || 0).toLocaleString()}</span>
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
