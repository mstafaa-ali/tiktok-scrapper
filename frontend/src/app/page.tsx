import type { Metadata } from "next";
import { HeroScrapeForm } from "@/features/scraping/hero-scrape-form";
import { RecentActivity } from "@/features/dashboard/recent-activity";

export const metadata: Metadata = {
  title: "Home | TikTok Scraper",
  description: "Scrape and analyze TikTok video comments",
};

export default function HomePage() {
  return (
    <div className="space-y-12 pb-8 animate-fade-in">
      <HeroScrapeForm />
      
      {/* Tampilkan recent activity di bawah agar pengguna masih bisa melihat history */}
      <div className="max-w-4xl mx-auto w-full">
        <div className="mb-4 px-2">
          <h2 className="text-xl font-semibold tracking-tight">Recent Scrapes</h2>
          <p className="text-sm text-muted-foreground">Aktifitas scraping terbaru Anda.</p>
        </div>
        <RecentActivity />
      </div>
    </div>
  );
}
