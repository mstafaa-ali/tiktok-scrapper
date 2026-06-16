export interface ScrapeRequest {
  video_url: string;
}

export interface ScrapeResponse {
  job_id: string;
  status: string;
  message: string;
}
