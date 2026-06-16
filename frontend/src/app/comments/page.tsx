import type { Metadata } from "next";
import { CommentsClient } from "./_components/comments-client";
import { Suspense } from "react";
import { PageSkeleton } from "@/components/ui/page-skeleton";

export const metadata: Metadata = {
  title: "Comments | TikTok Scraper",
  description: "Daftar komentar dari video TikTok",
};

export default function CommentsPage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
        <CommentsClient />
    </Suspense>
  );
}
