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
  const videosList = Array.isArray(videosData) ? videosData : videosData?.data ?? [];

  return (
    <div className="flex items-center gap-4">
      <Select
        value={selectedVideoId || "all"}
        onValueChange={(value) =>
          onVideoChange(value === "all" ? undefined : (value ?? undefined))
        }
      >
        <SelectTrigger className="w-[250px]">
          <SelectValue placeholder="Semua Video" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Semua Video</SelectItem>
          {videosList.map((video) => (
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
