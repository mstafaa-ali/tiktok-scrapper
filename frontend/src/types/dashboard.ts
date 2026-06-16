export interface DashboardStats {
  total_videos: number;
  total_comments: number;
  total_jobs: number;
  success_rate: number;
}

export interface RecentActivity {
  id: string;
  type: "scrape" | "video_added" | "comments_added";
  description: string;
  timestamp: string;
}
