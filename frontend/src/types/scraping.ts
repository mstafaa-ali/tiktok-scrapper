export interface ScrapeRequest {
  video_url: string;
  max_comments?: number;
}

export interface ScrapeResponse {
  job_id: string;
  status: string;
  message: string;
}
