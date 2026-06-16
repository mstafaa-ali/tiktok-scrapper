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
