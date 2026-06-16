import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/services/api";
import type { DashboardStats, RecentActivity } from "@/types/dashboard";

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: () => apiClient.get<DashboardStats>("/dashboard/stats"),
    refetchInterval: 30 * 1000, // Refetch setiap 30 detik
  });
}

export function useRecentActivity() {
  return useQuery({
    queryKey: ["dashboard", "activity"],
    queryFn: () => apiClient.get<RecentActivity[]>("/dashboard/activity"),
    refetchInterval: 15 * 1000, // Refetch setiap 15 detik
  });
}
