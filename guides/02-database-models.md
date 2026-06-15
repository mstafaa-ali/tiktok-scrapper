# Step 2 - Database Models & Migration

> Panduan membuat model database dan menjalankan migration.

**Prasyarat:** Pastikan Step 1 (Project Setup) sudah selesai.

---

## Checklist

- [x] Membuat model `Video`
- [x] Membuat model `Comment`
- [x] Membuat model `ScrapeJob`
- [x] Menjalankan migration pertama
- [x] Verifikasi tabel di database

---

## 2.1 Membuat Model Video

```python
# backend/app/models/video.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tiktok_video_id = Column(String(100), unique=True, nullable=False, index=True)
    url = Column(Text, nullable=False)
    author_username = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")
    scrape_jobs = relationship("ScrapeJob", back_populates="video", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Video(id={self.id}, tiktok_video_id={self.tiktok_video_id})>"
```

### Penjelasan Field

| Field             | Type      | Keterangan                          |
| ----------------- | --------- | ----------------------------------- |
| `id`              | UUID      | Primary key, auto-generated         |
| `tiktok_video_id` | VARCHAR   | ID video dari TikTok, unique        |
| `url`             | TEXT      | URL lengkap video                   |
| `author_username` | VARCHAR   | Username pembuat video              |
| `description`     | TEXT      | Deskripsi/caption video             |
| `created_at`      | TIMESTAMP | Waktu record dibuat                 |
| `updated_at`      | TIMESTAMP | Waktu record terakhir diupdate      |

---

## 2.2 Membuat Model Comment

```python
# backend/app/models/comment.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment_id = Column(String(100), unique=True, nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    username = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    comment_text = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    comment_created_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, username={self.username})>"
```

### Penjelasan Field

| Field                | Type      | Keterangan                          |
| -------------------- | --------- | ----------------------------------- |
| `id`                 | UUID      | Primary key, auto-generated         |
| `comment_id`         | VARCHAR   | ID komentar dari TikTok, unique     |
| `video_id`           | UUID      | Foreign key ke tabel `videos`       |
| `username`           | VARCHAR   | Username komentator                 |
| `display_name`       | VARCHAR   | Nama tampilan komentator            |
| `comment_text`       | TEXT      | Isi komentar                        |
| `likes_count`        | INTEGER   | Jumlah like pada komentar           |
| `reply_count`        | INTEGER   | Jumlah balasan pada komentar        |
| `comment_created_at` | TIMESTAMP | Waktu komentar dibuat di TikTok     |
| `scraped_at`         | TIMESTAMP | Waktu komentar di-scrape            |

### Relationship

```text
Video (1)
   │
   └─────< Comments (N)

Satu video memiliki banyak komentar.
Setiap komentar hanya milik satu video.
```

---

## 2.3 Membuat Model ScrapeJob

```python
# backend/app/models/scrape_job.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)
    total_comments = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    # Relationships
    video = relationship("Video", back_populates="scrape_jobs")

    def __repr__(self):
        return f"<ScrapeJob(id={self.id}, status={self.status})>"
```

### Status Flow

```text
PENDING  →  RUNNING  →  SUCCESS
                    ↘  FAILED
```

| Status    | Keterangan                        |
| --------- | --------------------------------- |
| `PENDING` | Job dibuat, belum mulai           |
| `RUNNING` | Proses scraping sedang berjalan   |
| `SUCCESS` | Scraping selesai, berhasil        |
| `FAILED`  | Scraping gagal                    |

---

## 2.4 Register Semua Model

Buat file untuk mengumpulkan semua model:

```python
# backend/app/models/__init__.py
from app.models.video import Video
from app.models.comment import Comment
from app.models.scrape_job import ScrapeJob

__all__ = ["Video", "Comment", "ScrapeJob"]
```

---

## 2.5 Menjalankan Migration

### Langkah-langkah

1. **Pastikan `env.py` sudah mengimport model**

   ```python
   # backend/app/migrations/env.py
   from app.models import Video, Comment, ScrapeJob  # Import semua model
   from app.database.connection import Base
   target_metadata = Base.metadata
   ```

2. **Generate migration**

   ```bash
   cd backend
   alembic revision --autogenerate -m "create initial tables"
   ```

3. **Review file migration yang di-generate**

   Cek di `backend/app/migrations/versions/` — pastikan tabel `videos`, `comments`, dan `scrape_jobs` ada.

4. **Jalankan migration**

   ```bash
   alembic upgrade head
   ```

5. **Verifikasi di PostgreSQL**

   ```sql
   \dt  -- List semua tabel
   \d videos
   \d comments
   \d scrape_jobs
   ```

---

## Verifikasi Step 2

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Model `Video`, `Comment`, dan `ScrapeJob` sudah dibuat
- [ ] Migration berhasil dijalankan tanpa error
- [ ] Tabel `videos`, `comments`, `scrape_jobs` sudah ada di database
- [ ] Foreign key `comments.video_id` → `videos.id` sudah benar
- [ ] Foreign key `scrape_jobs.video_id` → `videos.id` sudah benar
- [ ] Index pada `tiktok_video_id` dan `comment_id` sudah dibuat

---

> **Selanjutnya:** Lanjut ke [03-scraper-integration.md](./03-scraper-integration.md)
