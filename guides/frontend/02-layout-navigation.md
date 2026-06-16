# Step 2 - Layout & Navigasi

> Panduan untuk membangun layout utama aplikasi: Sidebar, Navbar, dan Main Layout.

---

## Checklist

- [ ] Buat MainLayout component
- [ ] Buat Sidebar component
- [ ] Buat Navbar component
- [ ] Integrasikan layout ke root layout
- [ ] Implementasi responsive sidebar (mobile)
- [ ] Implementasi navigasi antar halaman

---

## 2.1 Main Layout

### Tujuan

Menyediakan layout konsisten di seluruh halaman: sidebar di kiri, konten di kanan, navbar di atas.

### Struktur Visual

```text
┌──────────────────────────────────────────────┐
│                   Navbar                     │
├──────────┬───────────────────────────────────┤
│          │                                   │
│ Sidebar  │          Main Content             │
│          │                                   │
│          │                                   │
│          │                                   │
└──────────┴───────────────────────────────────┘
```

### File

```typescript
// frontend/src/components/layouts/main-layout.tsx
"use client";

import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

---

## 2.2 Sidebar

### Tujuan

Navigasi utama aplikasi. Menampilkan daftar menu halaman.

### Menu Items

| Icon     | Label       | Route        |
| -------- | ----------- | ------------ |
| 📊       | Dashboard   | `/`          |
| 🔄       | Scraping    | `/scraping`  |
| 🎬       | Videos      | `/videos`    |
| 💬       | Comments    | `/comments`  |
| 📋       | Jobs        | `/jobs`      |

### File

```typescript
// frontend/src/components/layouts/sidebar.tsx
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

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Download, label: "Scraping", href: "/scraping" },
  { icon: Video, label: "Videos", href: "/videos" },
  { icon: MessageSquare, label: "Comments", href: "/comments" },
  { icon: ListChecks, label: "Jobs", href: "/jobs" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 border-r bg-card md:block">
      {/* Logo / Brand */}
      <div className="flex h-14 items-center border-b px-6">
        <h1 className="text-lg font-bold">TikTok Scraper</h1>
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
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
```

### Dependency

Install icon library:

```bash
npm install lucide-react
```

---

## 2.3 Navbar

### Tujuan

Header di bagian atas konten utama. Menampilkan judul halaman, tombol toggle sidebar (mobile), dan info pengguna (opsional).

### File

```typescript
// frontend/src/components/layouts/navbar.tsx
"use client";

import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import { useUIStore } from "@/stores/ui-store";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/scraping": "Scraping",
  "/videos": "Videos",
  "/comments": "Comments",
  "/jobs": "Job Monitoring",
};

export function Navbar() {
  const pathname = usePathname();
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  const title = pageTitles[pathname] || "TikTok Scraper";

  return (
    <header className="flex h-14 items-center border-b px-6">
      {/* Mobile sidebar toggle */}
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={toggleSidebar}
      >
        <Menu className="h-5 w-5" />
      </Button>

      <h2 className="text-lg font-semibold">{title}</h2>
    </header>
  );
}
```

---

## 2.4 Mobile Sidebar (Sheet)

### Tujuan

Pada tampilan mobile, sidebar disembunyikan dan ditampilkan sebagai Sheet (overlay dari kiri).

### File

```typescript
// frontend/src/components/layouts/mobile-sidebar.tsx
"use client";

import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import { Sidebar } from "./sidebar";

export function MobileSidebar() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-64 p-0">
        <Sidebar />
      </SheetContent>
    </Sheet>
  );
}
```

---

## 2.5 Integrasikan ke Root Layout

### File

```typescript
// frontend/src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/lib/query-provider";
import { MainLayout } from "@/components/layouts/main-layout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TikTok Scraper",
  description: "Dashboard untuk scraping komentar video TikTok",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className={inter.className}>
        <QueryProvider>
          <MainLayout>{children}</MainLayout>
        </QueryProvider>
      </body>
    </html>
  );
}
```

---

## 2.6 Buat Placeholder Pages

Buat file halaman kosong untuk setiap route agar navigasi bisa diverifikasi.

### Dashboard

```typescript
// frontend/src/app/page.tsx
export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p className="text-muted-foreground">Ringkasan sistem akan ditampilkan di sini.</p>
    </div>
  );
}
```

### Scraping Page

```typescript
// frontend/src/app/scraping/page.tsx
export default function ScrapingPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Scraping</h1>
      <p className="text-muted-foreground">Form scraping akan ditampilkan di sini.</p>
    </div>
  );
}
```

### Videos Page

```typescript
// frontend/src/app/videos/page.tsx
export default function VideosPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Videos</h1>
      <p className="text-muted-foreground">Daftar video akan ditampilkan di sini.</p>
    </div>
  );
}
```

### Video Detail Page

```typescript
// frontend/src/app/videos/[id]/page.tsx
export default function VideoDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <div>
      <h1 className="text-2xl font-bold">Video Detail: {params.id}</h1>
      <p className="text-muted-foreground">Detail video akan ditampilkan di sini.</p>
    </div>
  );
}
```

### Comments Page

```typescript
// frontend/src/app/comments/page.tsx
export default function CommentsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Comments</h1>
      <p className="text-muted-foreground">Daftar komentar akan ditampilkan di sini.</p>
    </div>
  );
}
```

### Jobs Page

```typescript
// frontend/src/app/jobs/page.tsx
export default function JobsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Job Monitoring</h1>
      <p className="text-muted-foreground">Status job akan ditampilkan di sini.</p>
    </div>
  );
}
```

---

## Verifikasi Step 2

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Layout sidebar + navbar tampil di semua halaman
- [ ] Navigasi antar halaman berfungsi dengan benar
- [ ] Menu aktif di-highlight sesuai halaman yang sedang dibuka
- [ ] Mobile sidebar (Sheet) berfungsi pada tampilan kecil
- [ ] Semua placeholder pages bisa diakses via sidebar

---

> **Selanjutnya:** Lanjut ke [03-api-layer.md](./03-api-layer.md)
