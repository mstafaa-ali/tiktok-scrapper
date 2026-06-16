import { apiClient } from "./api";
import type { ScrapeJob, JobListResponse, JobListParams } from "@/types/job";

export const jobService = {
  getAll: async (params?: JobListParams): Promise<JobListResponse> => {
    const queryParams: Record<string, string> = {};
    if (params?.page) queryParams.page = String(params.page);
    if (params?.page_size) queryParams.page_size = String(params.page_size);
    if (params?.status) queryParams.status = params.status;
    if (params?.sort_by) queryParams.sort_by = params.sort_by;
    if (params?.sort_order) queryParams.sort_order = params.sort_order;

    return apiClient.get<JobListResponse>("/jobs", queryParams);
  },

  getById: async (id: string): Promise<ScrapeJob> => {
    return apiClient.get<ScrapeJob>(`/jobs/${id}`);
  },
};
