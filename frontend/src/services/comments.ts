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

  getExportUrl: (videoId?: string): string => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
    if (videoId) {
      return `${baseUrl}/comments/export?video_id=${videoId}`;
    }
    return `${baseUrl}/comments/export`;
  },
};
