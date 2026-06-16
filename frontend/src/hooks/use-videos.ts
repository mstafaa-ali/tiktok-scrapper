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
