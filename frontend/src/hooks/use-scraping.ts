import { useMutation, useQueryClient } from "@tanstack/react-query";
import { scrapingService } from "@/services/scraping";
import type { ScrapeRequest } from "@/types/scraping";

export function useScraping() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ScrapeRequest) => scrapingService.startScraping(data),
    onSuccess: () => {
      // Invalidate jobs & videos queries setelah scraping berhasil dimulai
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["videos"] });
    },
  });
}
