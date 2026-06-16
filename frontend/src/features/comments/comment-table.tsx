"use client";

import { DataTable, type Column } from "@/components/tables/data-table";
import type { Comment } from "@/types/comment";

const columns: Column<Comment>[] = [
  {
    key: "username",
    label: "Username",
    sortable: true,
    render: (comment) => (
      <div>
        <span className="font-medium">@{comment.username || "unknown"}</span>
        {comment.display_name && (
          <p className="text-xs text-muted-foreground">{comment.display_name}</p>
        )}
      </div>
    ),
  },
  {
    key: "comment_text",
    label: "Comment",
    render: (comment) => (
      <div className="max-w-[400px]">
        <p className="line-clamp-2 text-sm">{comment.comment_text}</p>
      </div>
    ),
  },
  {
    key: "likes_count",
    label: "Likes",
    sortable: true,
    render: (comment) => (
      <span className="text-sm">{(comment.likes_count || 0).toLocaleString()}</span>
    ),
  },
  {
    key: "reply_count",
    label: "Replies",
    sortable: true,
    render: (comment) => (
      <span className="text-sm">{(comment.reply_count || 0).toLocaleString()}</span>
    ),
  },
  {
    key: "comment_created_at",
    label: "Tanggal",
    sortable: true,
    render: (comment) => (
      <span className="text-xs text-muted-foreground">
        {comment.comment_created_at 
          ? new Date(comment.comment_created_at).toLocaleDateString("id-ID") 
          : new Date(comment.scraped_at).toLocaleDateString("id-ID")}
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
