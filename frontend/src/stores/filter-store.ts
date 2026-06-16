import { create } from "zustand";
import { persist } from "zustand/middleware";

interface FilterState {
  videosPageSize: number;
  commentsPageSize: number;
  jobsPageSize: number;
  setVideosPageSize: (size: number) => void;
  setCommentsPageSize: (size: number) => void;
  setJobsPageSize: (size: number) => void;
}

export const useFilterStore = create<FilterState>()(
  persist(
    (set) => ({
      videosPageSize: 10,
      commentsPageSize: 20,
      jobsPageSize: 15,
      setVideosPageSize: (size) => set({ videosPageSize: size }),
      setCommentsPageSize: (size) => set({ commentsPageSize: size }),
      setJobsPageSize: (size) => set({ jobsPageSize: size }),
    }),
    {
      name: "tiktok-scraper-filters",
    }
  )
);
