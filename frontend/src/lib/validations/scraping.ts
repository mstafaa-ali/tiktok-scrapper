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
  maxComments: z
    .number({ message: "Harus berupa angka" })
    .min(1, "Minimal 1 komentar")
    .max(10000, "Maksimal 10000 komentar"),
});

export type ScrapingFormValues = z.infer<typeof scrapingFormSchema>;
