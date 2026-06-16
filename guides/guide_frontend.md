# Frontend System Design

# Overview

Frontend bertanggung jawab untuk:

- Mengelola proses scraping video TikTok
- Menampilkan status scraping
- Menampilkan daftar video yang telah diproses
- Menampilkan komentar yang tersimpan
- Melakukan pencarian dan filtering data
- Menyediakan dashboard monitoring proses scraping

---

# Technology Stack

## Framework

### Next.js 15

Alasan:

- App Router
- Server Components
- SEO Friendly
- Mudah integrasi dengan API Backend

---

## Styling

### Tailwind CSS

Alasan:

- Utility First
- Konsisten
- Cepat untuk pengembangan dashboard

---

## State Management

### Zustand

Digunakan untuk:

- User Preferences
- Filter State
- Global UI State

Data utama tetap berasal dari API.

---

## Data Fetching

### TanStack Query

Digunakan untuk:

- Caching
- Background Refetch
- Pagination
- Loading State
- Error State

---

## Form Validation

### React Hook Form

### Zod

Digunakan untuk:

- Input URL video
- Filter data

---

# High Level Architecture

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

# Project Structure

```text
src/

├── app/
│
├── components/
│   ├── ui/
│   ├── layouts/
│   ├── tables/
│   └── charts/
│
├── features/
│   ├── dashboard/
│   ├── videos/
│   ├── comments/
│   └── scraping/
│
├── services/
│   ├── api.ts
│   ├── comments.ts
│   ├── videos.ts
│   └── jobs.ts
│
├── stores/
│
├── hooks/
│
├── types/
│
├── lib/
│
└── constants/
```

---

# Page Structure

## Dashboard

### Route

```text
/
```

### Tujuan

Memberikan ringkasan sistem.

### Widget

- Total Video
- Total Komentar
- Total Scraping Jobs
- Success Rate
- Recent Activity

---

## Scraping Page

### Route

```text
/scraping
```

### Fitur

Input URL TikTok.

Form:

```text
Video URL
[Start Scraping]
```

Setelah submit:

```text
Job Created
Status: RUNNING
```

Progress akan diperbarui secara berkala.

---

## Video List

### Route

```text
/videos
```

### Tabel

| Video | Author | Comments | Last Scrape |
| ----- | ------ | -------- | ----------- |

Fitur:

- Pagination
- Search
- Sort

---

## Video Detail

### Route

```text
/videos/[id]
```

### Informasi

Metadata video.

```text
Video Information
Scraping History
Comments Count
```

---

## Comments Page

### Route

```text
/comments
```

### Tabel

| Username | Comment | Likes | Replies |
| -------- | ------- | ----- | ------- |

Fitur:

- Pagination
- Search
- Filter

---

## Job Monitoring

### Route

```text
/jobs
```

### Tabel

| Job ID | Status | Started | Finished |
| ------ | ------ | ------- | -------- |

Status:

```text
RUNNING
SUCCESS
FAILED
```

---

# API Layer

## videos.service.ts

Endpoint:

```text
GET /videos
GET /videos/:id
```

---

## comments.service.ts

Endpoint:

```text
GET /comments
GET /comments/search
```

---

## jobs.service.ts

Endpoint:

```text
GET /jobs
GET /jobs/:id
```

---

## scraping.service.ts

Endpoint:

```text
POST /videos/scrape
```

---

# State Management

## Zustand

Digunakan untuk:

```text
Sidebar State
Theme State
Search Filter State
Table Preference
```

Tidak digunakan untuk:

```text
Video Data
Comment Data
Job Data
```

Karena data tersebut dikelola oleh TanStack Query.

---

# UI Components

## Reusable Components

```text
Button
Input
Select
Modal
Drawer
Badge
Card
```

---

## Table Components

```text
DataTable
Pagination
ColumnFilter
SearchInput
```

---

# Error Handling

## Loading State

Gunakan skeleton loading.

---

## Empty State

Contoh:

```text
No comments found
```

---

## Error State

Contoh:

```text
Failed to load comments
```

---

# Development Roadmap

## Phase 1

- Setup Next.js
- Setup Tailwind
- Setup Shadcn UI
- Setup Zustand
- Setup TanStack Query

---

## Phase 2

- Layout Dashboard
- Sidebar
- Navbar

---

## Phase 3

- Dashboard Page
- Scraping Page

---

## Phase 4

- Videos Page
- Video Detail Page

---

## Phase 5

- Comments Page
- Search & Filter

---

## Phase 6

- Job Monitoring
- Error Handling
- Optimization

```

```
