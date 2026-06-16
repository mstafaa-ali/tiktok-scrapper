"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Download,
  Video,
  MessageSquare,
  ListChecks,
} from "lucide-react";
import { useUIStore } from "@/stores/ui-store";

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Download, label: "Scraping", href: "/scraping" },
  { icon: Video, label: "Videos", href: "/videos" },
  { icon: MessageSquare, label: "Comments", href: "/comments" },
  { icon: ListChecks, label: "Jobs", href: "/jobs" },
];

export function Sidebar() {
  const pathname = usePathname();
  const sidebarOpen = useUIStore((state) => state.sidebarOpen);

  return (
    <aside
      className={cn(
        "hidden w-64 border-r bg-card md:block transition-all duration-300",
        !sidebarOpen && "w-0 overflow-hidden border-none"
      )}
    >
      {/* Logo / Brand */}
      <div className="flex h-14 items-center border-b px-6">
        <h1 className="text-lg font-bold min-w-max">TikTok Scraper</h1>
      </div>

      {/* Navigation */}
      <nav className="space-y-1 p-4">
        {menuItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              <span className="min-w-max">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
