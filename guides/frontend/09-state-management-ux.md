# Step 9 - State Management & UX Polish

> Panduan untuk mengimplementasikan Zustand stores, dark mode, dan peningkatan UX secara keseluruhan.

---

## Checklist

- [ ] Buat Zustand stores (UI, Filter, Table Preferences)
- [ ] Implementasi dark mode toggle
- [ ] Implementasi persist state (localStorage)
- [ ] Tambahkan toast notifications
- [ ] Tambahkan loading transitions antar halaman
- [ ] Implementasi breadcrumbs di halaman detail

---

## 9.1 Zustand Stores

### Prinsip Penggunaan

Zustand **hanya** digunakan untuk:

| ✅ Digunakan untuk         | ❌ TIDAK digunakan untuk |
| -------------------------- | ----------------------- |
| Sidebar open/close state   | Video data              |
| Theme (dark/light)         | Comment data            |
| Search/filter preferences  | Job data                |
| Table column preferences   | Dashboard stats         |

Data dari server **selalu** dikelola oleh TanStack Query.

---

### UI Store

```typescript
// frontend/src/stores/ui-store.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UIState {
  sidebarOpen: boolean;
  theme: "light" | "dark" | "system";
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: "light" | "dark" | "system") => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: "system",
      toggleSidebar: () =>
        set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: "tiktok-scraper-ui",
    }
  )
);
```

### Filter Store

```typescript
// frontend/src/stores/filter-store.ts
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
```

---

## 9.2 Dark Mode

### Tujuan

Mendukung 3 mode tema: Light, Dark, dan System (mengikuti preferensi OS).

### Theme Provider

```typescript
// frontend/src/lib/theme-provider.tsx
"use client";

import { useEffect } from "react";
import { useUIStore } from "@/stores/ui-store";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useUIStore((state) => state.theme);

  useEffect(() => {
    const root = document.documentElement;

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";
      root.classList.toggle("dark", systemTheme === "dark");
    } else {
      root.classList.toggle("dark", theme === "dark");
    }
  }, [theme]);

  return <>{children}</>;
}
```

### Theme Toggle Button

```typescript
// frontend/src/components/layouts/theme-toggle.tsx
"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sun, Moon, Monitor } from "lucide-react";
import { useUIStore } from "@/stores/ui-store";

export function ThemeToggle() {
  const { theme, setTheme } = useUIStore();

  const icon = {
    light: Sun,
    dark: Moon,
    system: Monitor,
  }[theme];

  const Icon = icon;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <Icon className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          <Sun className="mr-2 h-4 w-4" />
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          <Moon className="mr-2 h-4 w-4" />
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          <Monitor className="mr-2 h-4 w-4" />
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

### Integrasikan ke Navbar

Tambahkan `ThemeToggle` di navbar:

```typescript
// Update frontend/src/components/layouts/navbar.tsx
// Tambahkan ThemeToggle di sebelah kanan navbar
import { ThemeToggle } from "./theme-toggle";

// Di dalam return:
<header className="flex h-14 items-center justify-between border-b px-6">
  <div className="flex items-center gap-2">
    {/* Mobile sidebar toggle */}
    {/* Page title */}
  </div>
  <ThemeToggle />
</header>
```

### Integrasikan ThemeProvider ke Root Layout

```typescript
// Update frontend/src/app/layout.tsx
import { ThemeProvider } from "@/lib/theme-provider";

// Bungkus children dengan ThemeProvider
<QueryProvider>
  <ThemeProvider>
    <MainLayout>{children}</MainLayout>
  </ThemeProvider>
</QueryProvider>
```

---

## 9.3 Toast Notifications

### Tujuan

Memberikan feedback visual kepada user untuk aksi-aksi penting (scraping dimulai, error, dll.).

### Setup

Shadcn toast sudah terinstall di Step 1. Pastikan Toaster component ada di layout.

```typescript
// Tambahkan di frontend/src/app/layout.tsx
import { Toaster } from "@/components/ui/toast";

// Di dalam body:
<body>
  <QueryProvider>
    <ThemeProvider>
      <MainLayout>{children}</MainLayout>
      <Toaster />
    </ThemeProvider>
  </QueryProvider>
</body>
```

### Penggunaan di Scraping

```typescript
// Update scraping form onSuccess & onError
import { useToast } from "@/components/ui/use-toast";

const { toast } = useToast();

// onSuccess
toast({
  title: "Scraping dimulai!",
  description: `Job ID: ${result.job_id}`,
});

// onError
toast({
  title: "Gagal memulai scraping",
  description: "Silakan periksa URL dan coba lagi.",
  variant: "destructive",
});
```

---

## 9.4 Breadcrumbs

### Tujuan

Menunjukkan navigasi hierarki di halaman detail (contoh: Videos > Video Detail).

### File

```typescript
// frontend/src/components/layouts/breadcrumbs.tsx
"use client";

import Link from "next/link";
import { ChevronRight } from "lucide-react";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <nav className="flex items-center gap-1 text-sm text-muted-foreground">
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-1">
          {index > 0 && <ChevronRight className="h-3 w-3" />}
          {item.href ? (
            <Link
              href={item.href}
              className="hover:text-foreground transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}
```

### Penggunaan di Video Detail

```typescript
// Di video detail page
<Breadcrumbs
  items={[
    { label: "Videos", href: "/videos" },
    { label: video.description || `Video ${video.id}` },
  ]}
/>
```

---

## 9.5 Loading Transition

### Tujuan

Menambahkan animasi halus saat berpindah halaman atau memuat data.

### CSS Transitions

Tambahkan di `globals.css`:

```css
/* Fade-in animation for page content */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
```

### Gunakan di Main Layout

```typescript
// Di main-layout.tsx
<main className="flex-1 overflow-y-auto p-6">
  <div className="animate-fade-in">
    {children}
  </div>
</main>
```

---

## Verifikasi Step 9

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Dark mode toggle berfungsi (Light, Dark, System)
- [ ] Tema tersimpan di localStorage (persist setelah refresh)
- [ ] Sidebar state tersimpan di localStorage
- [ ] Toast notification muncul saat scraping dimulai/gagal
- [ ] Breadcrumbs tampil di halaman detail
- [ ] Fade-in animation berjalan saat berpindah halaman
- [ ] Page size preferences tersimpan

---

> **Selanjutnya:** Lanjut ke [10-error-handling-optimization.md](./10-error-handling-optimization.md)
