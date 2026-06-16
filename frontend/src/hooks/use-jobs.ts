import { useQuery } from "@tanstack/react-query";
import { jobService } from "@/services/jobs";
import type { JobListParams } from "@/types/job";

export function useJobs(params?: JobListParams) {
  return useQuery({
    queryKey: ["jobs", params],
    queryFn: () => jobService.getAll(params),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.data.some((job) => job.status === "RUNNING")) return 5000;
      return false;
    },
  });
}

export function useJob(id: string) {
  return useQuery({
    queryKey: ["job", id],
    queryFn: () => jobService.getById(id),
    enabled: !!id,
    refetchInterval: (query) => {
      // Auto-refetch setiap 5 detik jika status masih RUNNING
      const data = query.state.data;
      if (data && data.status === "RUNNING") return 5000;
      return false;
    },
  });
}
