import { z } from "zod";

export const scrapingFormSchema = z.object({
  videoUrl: z
    .string()
    .min(1, "URL video wajib diisi")
    .url("Format URL tidak valid")
    .refine(
      (url) => {
        // Menerima berbagai format URL TikTok
        return (
          url.includes("tiktok.com") ||
          url.includes("vm.tiktok.com") ||
          url.includes("vt.tiktok.com")
        );
      },
      "URL harus dari TikTok (tiktok.com)"
    ),
});

export type ScrapingFormValues = z.infer<typeof scrapingFormSchema>;
