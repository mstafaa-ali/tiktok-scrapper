"use client";

import { useVideo } from "@/hooks/use-videos";
import { Breadcrumbs } from "@/components/layouts/breadcrumbs";
import { Loader2 } from "lucide-react";
import { useParams } from "next/navigation";

export default function VideoDetailPage() {
  const params = useParams<{ id: string }>();
  const { data: video, isLoading, isError } = useVideo(params.id);

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !video) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-destructive">
        Video tidak ditemukan atau terjadi kesalahan.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: "Videos", href: "/videos" },
          { label: video.description || `Video ${video.id}` },
        ]}
      />
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Video Detail</h1>
        <p className="text-muted-foreground">
          {video.description || `Video ID: ${video.id}`}
        </p>
      </div>

      {/* Tampilkan detail video lainnya di sini */}
    </div>
  );
}
