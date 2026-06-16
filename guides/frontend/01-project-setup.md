# Step 1 - Project Setup & Konfigurasi

> Panduan lengkap untuk menyiapkan seluruh fondasi project frontend.

---

## Checklist

- [ ] Inisialisasi Next.js 15 project
- [ ] Setup Tailwind CSS
- [ ] Setup Shadcn UI
- [ ] Install & konfigurasi Zustand
- [ ] Install & konfigurasi TanStack Query
- [ ] Install React Hook Form & Zod
- [ ] Setup environment variables
- [ ] Buat struktur folder lengkap

---

## 1.1 Inisialisasi Next.js 15

### Langkah-langkah

1. **Buat project Next.js**

   ```bash
   npx -y create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
   ```

   > Gunakan opsi default untuk konfigurasi lainnya.

2. **Masuk ke folder project**

   ```bash
   cd frontend
   ```

3. **Jalankan development server**

   ```bash
   npm run dev
   ```

4. **Verifikasi**
   - Buka `http://localhost:3000` → halaman default Next.js harus tampil

---

## 1.2 Setup Tailwind CSS

> Tailwind CSS sudah terinstall otomatis saat inisialisasi Next.js dengan flag `--tailwind`.

### Langkah-langkah

1. **Verifikasi file `tailwind.config.ts`**

   Pastikan konfigurasi content path sudah benar:

   ```typescript
   // frontend/tailwind.config.ts
   import type { Config } from "tailwindcss";

   const config: Config = {
     darkMode: ["class"],
     content: [
       "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
       "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
       "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
       "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
     ],
     theme: {
       extend: {
         colors: {
           // Custom colors akan ditambahkan sesuai kebutuhan
         },
       },
     },
     plugins: [],
   };

   export default config;
   ```

2. **Verifikasi `globals.css`**

   Pastikan directive Tailwind ada di `src/app/globals.css`:

   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

---

## 1.3 Setup Shadcn UI

### Langkah-langkah

1. **Inisialisasi Shadcn UI**

   ```bash
   npx -y shadcn@latest init
   ```

   Pilih konfigurasi berikut saat ditanya:
   - Style: **Default**
   - Base color: **Slate**
   - CSS variables: **Yes**

2. **Install komponen dasar yang dibutuhkan**

   ```bash
   npx -y shadcn@latest add button
   npx -y shadcn@latest add input
   npx -y shadcn@latest add select
   npx -y shadcn@latest add dialog
   npx -y shadcn@latest add sheet
   npx -y shadcn@latest add badge
   npx -y shadcn@latest add card
   npx -y shadcn@latest add table
   npx -y shadcn@latest add skeleton
   npx -y shadcn@latest add toast
   npx -y shadcn@latest add dropdown-menu
   npx -y shadcn@latest add separator
   npx -y shadcn@latest add tooltip
   ```

3. **Verifikasi**
   - Folder `src/components/ui/` harus terisi komponen Shadcn
   - File `lib/utils.ts` harus ada

---

## 1.4 Install & Konfigurasi Zustand

### Langkah-langkah

1. **Install Zustand**

   ```bash
   npm install zustand
   ```

2. **Buat contoh store dasar**

   ```typescript
   // frontend/src/stores/ui-store.ts
   import { create } from "zustand";

   interface UIState {
     sidebarOpen: boolean;
     theme: "light" | "dark";
     toggleSidebar: () => void;
     setTheme: (theme: "light" | "dark") => void;
   }

   export const useUIStore = create<UIState>((set) => ({
     sidebarOpen: true,
     theme: "light",
     toggleSidebar: () =>
       set((state) => ({ sidebarOpen: !state.sidebarOpen })),
     setTheme: (theme) => set({ theme }),
   }));
   ```

---

## 1.5 Install & Konfigurasi TanStack Query

### Langkah-langkah

1. **Install TanStack Query**

   ```bash
   npm install @tanstack/react-query @tanstack/react-query-devtools
   ```

2. **Buat QueryClient Provider**

   ```typescript
   // frontend/src/lib/query-provider.tsx
   "use client";

   import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
   import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
   import { useState } from "react";

   export function QueryProvider({ children }: { children: React.ReactNode }) {
     const [queryClient] = useState(
       () =>
         new QueryClient({
           defaultOptions: {
             queries: {
               staleTime: 60 * 1000, // 1 menit
               retry: 1,
               refetchOnWindowFocus: false,
             },
           },
         })
     );

     return (
       <QueryClientProvider client={queryClient}>
         {children}
         <ReactQueryDevtools initialIsOpen={false} />
       </QueryClientProvider>
     );
   }
   ```

3. **Integrasikan ke root layout**

   ```typescript
   // frontend/src/app/layout.tsx
   import { QueryProvider } from "@/lib/query-provider";

   export default function RootLayout({
     children,
   }: {
     children: React.ReactNode;
   }) {
     return (
       <html lang="id">
         <body>
           <QueryProvider>{children}</QueryProvider>
         </body>
       </html>
     );
   }
   ```

---

## 1.6 Install React Hook Form & Zod

### Langkah-langkah

1. **Install dependencies**

   ```bash
   npm install react-hook-form zod @hookform/resolvers
   ```

2. **Contoh schema validasi**

   ```typescript
   // frontend/src/lib/validations/scraping.ts
   import { z } from "zod";

   export const scrapingFormSchema = z.object({
     videoUrl: z
       .string()
       .min(1, "URL video wajib diisi")
       .url("Format URL tidak valid")
       .refine(
         (url) => url.includes("tiktok.com"),
         "URL harus dari TikTok"
       ),
   });

   export type ScrapingFormValues = z.infer<typeof scrapingFormSchema>;
   ```

---

## 1.7 Setup Environment Variables

### Langkah-langkah

1. **Buat file `.env.local`**

   ```env
   # Backend API
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # App
   NEXT_PUBLIC_APP_NAME=TikTok Scraper
   ```

2. **Buat file `.env.example`** (untuk referensi tim)

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_NAME=TikTok Scraper
   ```

3. **Pastikan `.env.local` ada di `.gitignore`**

   ```gitignore
   .env.local
   ```

---

## 1.8 Buat Struktur Folder Lengkap

### Langkah-langkah

Jalankan perintah berikut untuk membuat seluruh folder yang dibutuhkan:

```bash
# Dari folder frontend/

# Components
mkdir -p src/components/ui
mkdir -p src/components/layouts
mkdir -p src/components/tables
mkdir -p src/components/charts

# Features
mkdir -p src/features/dashboard
mkdir -p src/features/videos
mkdir -p src/features/comments
mkdir -p src/features/scraping
mkdir -p src/features/jobs

# Services
mkdir -p src/services

# Lainnya
mkdir -p src/hooks
mkdir -p src/stores
mkdir -p src/types
mkdir -p src/lib/validations
mkdir -p src/constants
```

---

## Verifikasi Step 1

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] `npm run dev` berjalan tanpa error di `http://localhost:3000`
- [ ] Shadcn UI komponen sudah terinstall di `src/components/ui/`
- [ ] File `src/lib/query-provider.tsx` sudah dibuat
- [ ] File `src/stores/ui-store.ts` sudah dibuat
- [ ] File `.env.local` sudah dikonfigurasi
- [ ] Seluruh folder project sudah terbuat sesuai struktur

---

> **Selanjutnya:** Lanjut ke [02-layout-navigation.md](./02-layout-navigation.md)
