export type JobStatus = "PENDING" | "RUNNING" | "SUCCESS" | "FAILED";

export interface ScrapeJob {
  id: string;
  video_id: string;
  video_url: string;
  status: JobStatus;
  target_comments: number;
  comments_scraped: number;
  error_message: string | null;
  started_at: string;
  finished_at: string | null;
  created_at: string;
}

export interface JobListResponse {
  data: ScrapeJob[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface JobListParams {
  page?: number;
  page_size?: number;
  status?: JobStatus;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}
