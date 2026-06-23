import { apiClient } from "./api";
import type { ScrapeRequest, ScrapeResponse } from "@/types/scraping";

export const scrapingService = {
  startScraping: async (data: ScrapeRequest): Promise<ScrapeResponse> => {
    return apiClient.post<ScrapeResponse>("/videos/scrape", { url: data.video_url, max_comments: data.max_comments ?? 100 });
  },
};
