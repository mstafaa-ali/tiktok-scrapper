export interface Comment {
  id: string;
  comment_id: string;
  video_id: string;
  username: string | null;
  display_name: string | null;
  comment_text: string;
  likes_count: number;
  reply_count: number;
  comment_created_at: string | null;
  scraped_at: string;
}

export interface CommentListResponse {
  data: Comment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CommentListParams {
  page?: number;
  page_size?: number;
  search?: string;
  video_id?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}
