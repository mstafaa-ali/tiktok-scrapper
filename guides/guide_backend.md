# Backend System Design

## Overview

Backend bertanggung jawab untuk:

- Mengambil komentar dari video TikTok
- Menyimpan hasil scraping ke database
- Menyediakan API untuk frontend
- Mengelola riwayat proses scraping
- Menyediakan data komentar yang telah tersimpan

## High Level Architecture

```text
┌─────────────┐
│  Frontend   │
│  Next.js    │
└──────┬──────┘
       │ REST API
       ▼
┌─────────────┐
│  FastAPI    │
│ Backend API │
└──────┬──────┘
       │
 ┌─────┴──────────┐
 │                │
 ▼                ▼
PostgreSQL     Scraper Service
(Database)      (TikTokApi)
```

---

# Technology Stack

## Backend Framework

### FastAPI

Alasan:

- Mendukung asynchronous programming
- Performa tinggi
- Dokumentasi Swagger otomatis
- Mudah diintegrasikan dengan Python ecosystem

## ORM

### SQLAlchemy 2.0

Alasan:

- ORM yang stabil dan mature
- Mendukung PostgreSQL dengan baik
- Mudah digunakan bersama Alembic

## Database

### PostgreSQL

Alasan:

- Cocok untuk data terstruktur
- Mendukung indexing dan query kompleks
- Skalabel untuk data dalam jumlah besar

## Migration Tool

### Alembic

Digunakan untuk:

- Versioning database schema
- Migrasi struktur database

## Scraper

### TikTokApi

Digunakan sebagai sumber utama pengambilan data komentar TikTok.

---

# Project Structure

```text
backend/

├── app/
│
├── api/
│   ├── videos.py
│   ├── comments.py
│   └── jobs.py
│
├── services/
│   ├── scraper_service.py
│   ├── comment_service.py
│   └── video_service.py
│
├── models/
│   ├── video.py
│   ├── comment.py
│   └── scrape_job.py
│
├── schemas/
│
├── database/
│
├── core/
│
├── migrations/
│
├── logs/
│
└── main.py
```

---

# Layer Architecture

```text
API Layer
    ↓
Service Layer
    ↓
Repository / Database Layer
    ↓
PostgreSQL
```

Prinsip:

- Endpoint tidak boleh langsung mengakses database.
- Seluruh business logic ditempatkan pada service layer.

---

# Database Design

## videos

Menyimpan informasi video TikTok.

| Field           | Type      |
| --------------- | --------- |
| id              | UUID      |
| tiktok_video_id | VARCHAR   |
| url             | TEXT      |
| author_username | VARCHAR   |
| description     | TEXT      |
| created_at      | TIMESTAMP |
| updated_at      | TIMESTAMP |

---

## comments

Menyimpan seluruh komentar yang berhasil diperoleh.

| Field              | Type      |
| ------------------ | --------- |
| id                 | UUID      |
| comment_id         | VARCHAR   |
| video_id           | UUID      |
| username           | VARCHAR   |
| display_name       | VARCHAR   |
| comment_text       | TEXT      |
| likes_count        | INTEGER   |
| reply_count        | INTEGER   |
| comment_created_at | TIMESTAMP |
| scraped_at         | TIMESTAMP |

### Relationship

```text
Video (1)
   │
   └─────< Comments (N)
```

---

## scrape_jobs

Mencatat proses scraping.

| Field          | Type      |
| -------------- | --------- |
| id             | UUID      |
| video_id       | UUID      |
| status         | VARCHAR   |
| total_comments | INTEGER   |
| started_at     | TIMESTAMP |
| finished_at    | TIMESTAMP |

### Status

```text
PENDING
RUNNING
SUCCESS
FAILED
```

---

# Service Design

## Scraper Service

Tanggung jawab:

- Mengambil komentar dari TikTok
- Mengubah data mentah menjadi format internal

Input:

```python
video_url
```

Output:

```python
[
    {
        "comment_id": "...",
        "username": "...",
        "comment_text": "...",
        "likes_count": 10
    }
]
```

---

## Comment Service

Tanggung jawab:

- Menyimpan komentar
- Mengambil komentar
- Melakukan pencarian komentar
- Mengelola validasi data

---

## Video Service

Tanggung jawab:

- Menyimpan metadata video
- Mengambil data video
- Mengelola riwayat scraping

---

# API Design

## Trigger Scraping

### Endpoint

```http
POST /api/videos/scrape
```

Request

```json
{
  "url": "https://www.tiktok.com/..."
}
```

Response

```json
{
  "job_id": "uuid",
  "status": "RUNNING"
}
```

---

## Get Video

### Endpoint

```http
GET /api/videos/{video_id}
```

---

## Get Comments

### Endpoint

```http
GET /api/comments
```

Query Parameter

```text
?page=1
&limit=100
&video_id={video_id}
```

---

## Search Comments

### Endpoint

```http
GET /api/comments/search
```

Query Parameter

```text
?q=keyword
```

---

## Get Job Status

### Endpoint

```http
GET /api/jobs/{job_id}
```

---

# Error Handling

Standar response error:

```json
{
  "success": false,
  "message": "Video not found"
}
```

Standar response success:

```json
{
  "success": true,
  "data": {}
}
```

---

# Logging

Direktori:

```text
logs/
```

File:

```text
api.log
scraper.log
```

Data yang dicatat:

- Proses scraping dimulai
- Proses scraping selesai
- Jumlah komentar yang diperoleh
- Error saat scraping
- Error API

---

# Development Roadmap

## Phase 1 - Project Setup

- Setup FastAPI
- Setup PostgreSQL
- Setup SQLAlchemy
- Setup Alembic
- Setup Docker

## Phase 2 - Database

- Membuat model videos
- Membuat model comments
- Membuat model scrape_jobs
- Menjalankan migration

## Phase 3 - Scraper Integration

- Integrasi TikTokApi
- Mengambil komentar dari video
- Menyimpan hasil scraping

## Phase 4 - API Development

- Endpoint scraping
- Endpoint comments
- Endpoint videos
- Endpoint jobs

## Phase 5 - Testing

- Unit testing
- Integration testing
- Load testing

---

# Initial Development Order

Urutan implementasi yang direkomendasikan:

1. Setup FastAPI
2. Setup PostgreSQL
3. Setup SQLAlchemy
4. Setup Alembic
5. Membuat model database
6. Menjalankan migration
7. Membuat CRUD dasar
8. Integrasi TikTokApi
9. Membuat endpoint scraping
10. Menambahkan logging dan testing

```

```
