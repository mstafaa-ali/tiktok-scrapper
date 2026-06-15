# Step 0 - Overview & Arsitektur

> Dokumen ini berisi gambaran besar sistem. Baca ini terlebih dahulu sebelum memulai pengerjaan.

---

## Tujuan Sistem

Backend bertanggung jawab untuk:

- Mengambil komentar dari video TikTok
- Menyimpan hasil scraping ke database
- Menyediakan API untuk frontend
- Mengelola riwayat proses scraping
- Menyediakan data komentar yang telah tersimpan

---

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

## Layer Architecture

```text
API Layer
    ↓
Service Layer
    ↓
Repository / Database Layer
    ↓
PostgreSQL
```

**Prinsip:**

- Endpoint **tidak boleh** langsung mengakses database.
- Seluruh business logic ditempatkan pada **service layer**.

---

## Technology Stack

| Komponen         | Teknologi       | Alasan                                              |
| ---------------- | --------------- | --------------------------------------------------- |
| Backend Framework | FastAPI         | Async, performa tinggi, Swagger otomatis             |
| ORM              | SQLAlchemy 2.0  | Stabil, mature, integrasi Alembic                    |
| Database         | PostgreSQL      | Data terstruktur, indexing, skalabel                 |
| Migration        | Alembic         | Versioning schema, migrasi struktur                  |
| Scraper          | TikTokApi       | Sumber utama pengambilan data komentar TikTok        |

---

## Project Structure

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

## Development Roadmap

| Phase | Nama                   | Guide File                    |
| ----- | ---------------------- | ----------------------------- |
| 1     | Project Setup          | `01-project-setup.md`         |
| 2     | Database & Models      | `02-database-models.md`       |
| 3     | Scraper Integration    | `03-scraper-integration.md`   |
| 4     | API Development        | `04-api-development.md`       |
| 5     | Error Handling & Logging | `05-error-handling-logging.md` |
| 6     | Testing                | `06-testing.md`               |

---

## Urutan Pengerjaan

> Ikuti urutan ini untuk pengerjaan yang optimal:

1. ✅ Baca overview ini
2. 📖 Lanjut ke `01-project-setup.md`
3. 📖 Lalu `02-database-models.md`
4. 📖 Lalu `03-scraper-integration.md`
5. 📖 Lalu `04-api-development.md`
6. 📖 Lalu `05-error-handling-logging.md`
7. 📖 Lalu `06-testing.md`
