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
