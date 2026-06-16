# Step 0 - Overview & Arsitektur Frontend

> Dokumen ini berisi gambaran besar sistem frontend. Baca ini terlebih dahulu sebelum memulai pengerjaan.

---

## Tujuan Sistem

Frontend bertanggung jawab untuk:

- Mengelola proses scraping video TikTok
- Menampilkan status scraping secara real-time
- Menampilkan daftar video yang telah diproses
- Menampilkan komentar yang tersimpan
- Melakukan pencarian dan filtering data
- Menyediakan dashboard monitoring proses scraping

---

## High Level Architecture

```text
┌─────────────────────┐
│      Next.js        │
├─────────────────────┤
│      Pages          │
├─────────────────────┤
│      Features       │
├─────────────────────┤
│      Services       │
├─────────────────────┤
│      API Client     │
└──────────┬──────────┘
           │
           ▼
     FastAPI Backend
```

---

## Layer Architecture

```text
Pages / Routes
    ↓
Feature Components (per domain)
    ↓
Custom Hooks (useVideos, useComments, dll.)
    ↓
Services / API Client
    ↓
FastAPI Backend
```

**Prinsip:**

- **Komponen page** hanya bertugas meng-compose feature components, bukan berisi logic langsung.
- **Feature components** berisi UI dan logic spesifik per domain (dashboard, videos, comments, scraping, jobs).
- **Custom hooks** menggunakan TanStack Query untuk data fetching, caching, dan state management data server.
- **Services** adalah satu-satunya layer yang berkomunikasi langsung dengan API backend.
- **Zustand** hanya digunakan untuk client-side state (UI preferences, filter state), bukan data dari server.

---

## Technology Stack

| Komponen          | Teknologi         | Alasan                                                  |
| ----------------- | ----------------- | ------------------------------------------------------- |
| Framework         | Next.js 15        | App Router, Server Components, SEO Friendly              |
| Styling           | Tailwind CSS      | Utility First, konsisten, cepat untuk dashboard          |
| UI Components     | Shadcn UI         | Komponen berkualitas, mudah dikustomisasi, berbasis Radix |
| State Management  | Zustand           | Ringan, simple API, hanya untuk client state             |
| Data Fetching     | TanStack Query    | Caching, background refetch, pagination, loading/error   |
| Form Validation   | React Hook Form   | Performa tinggi, minimal re-render                       |
| Schema Validation | Zod               | Type-safe, integrasi baik dengan React Hook Form         |

---

## Project Structure

```text
frontend/
└── src/
    ├── app/                    # Next.js App Router (pages & layouts)
    │   ├── layout.tsx          # Root layout
    │   ├── page.tsx            # Dashboard (/)
    │   ├── scraping/
    │   │   └── page.tsx        # Scraping page (/scraping)
    │   ├── videos/
    │   │   ├── page.tsx        # Video list (/videos)
    │   │   └── [id]/
    │   │       └── page.tsx    # Video detail (/videos/[id])
    │   ├── comments/
    │   │   └── page.tsx        # Comments page (/comments)
    │   └── jobs/
    │       └── page.tsx        # Job monitoring (/jobs)
    │
    ├── components/
    │   ├── ui/                 # Shadcn UI primitives (Button, Input, dll.)
    │   ├── layouts/            # Sidebar, Navbar, MainLayout
    │   ├── tables/             # DataTable, Pagination, ColumnFilter
    │   └── charts/             # Chart components untuk dashboard
    │
    ├── features/
    │   ├── dashboard/          # Dashboard widgets & logic
    │   ├── videos/             # Video list & detail components
    │   ├── comments/           # Comments table & filter components
    │   ├── scraping/           # Scraping form & progress components
    │   └── jobs/               # Job monitoring components
    │
    ├── services/
    │   ├── api.ts              # Base API client (axios/fetch config)
    │   ├── videos.ts           # Video API calls
    │   ├── comments.ts         # Comments API calls
    │   ├── jobs.ts             # Jobs API calls
    │   └── scraping.ts         # Scraping API calls
    │
    ├── hooks/                  # Custom hooks (useVideos, useComments, dll.)
    │
    ├── stores/                 # Zustand stores
    │
    ├── types/                  # TypeScript type definitions
    │
    ├── lib/                    # Utility functions
    │
    └── constants/              # App constants
```

---

## Page Routes

| Route           | Page            | Deskripsi                          |
| --------------- | --------------- | ---------------------------------- |
| `/`             | Dashboard       | Ringkasan statistik sistem          |
| `/scraping`     | Scraping        | Input URL & mulai scraping          |
| `/videos`       | Video List      | Daftar video yang telah di-scrape   |
| `/videos/[id]`  | Video Detail    | Detail metadata & komentar video    |
| `/comments`     | Comments        | Daftar komentar dengan search/filter|
| `/jobs`         | Job Monitoring  | Status & riwayat scraping jobs      |

---

## Development Roadmap

| Phase | Nama                              | Guide File                          |
| ----- | --------------------------------- | ----------------------------------- |
| 1     | Project Setup & Konfigurasi       | `01-project-setup.md`               |
| 2     | Layout & Navigasi                 | `02-layout-navigation.md`           |
| 3     | API Layer & Data Fetching         | `03-api-layer.md`                   |
| 4     | Dashboard Page                    | `04-dashboard.md`                   |
| 5     | Scraping Feature                  | `05-scraping.md`                    |
| 6     | Videos Feature                    | `06-videos.md`                      |
| 7     | Comments Feature                  | `07-comments.md`                    |
| 8     | Job Monitoring                    | `08-job-monitoring.md`              |
| 9     | State Management & UX Polish      | `09-state-management-ux.md`         |
| 10    | Error Handling & Optimization     | `10-error-handling-optimization.md` |

---

## Urutan Pengerjaan

> Ikuti urutan ini untuk pengerjaan yang optimal:

1. 📖 Baca overview ini
2. 📖 Lanjut ke `01-project-setup.md`
3. 📖 Lalu `02-layout-navigation.md`
4. 📖 Lalu `03-api-layer.md`
5. 📖 Lalu `04-dashboard.md`
6. 📖 Lalu `05-scraping.md`
7. 📖 Lalu `06-videos.md`
8. 📖 Lalu `07-comments.md`
9. 📖 Lalu `08-job-monitoring.md`
10. 📖 Lalu `09-state-management-ux.md`
11. 📖 Lalu `10-error-handling-optimization.md`
