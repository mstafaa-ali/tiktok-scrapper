# Step 4 - API Development

> Panduan membuat seluruh endpoint REST API.

**Prasyarat:** Pastikan Step 3 (Scraper Integration) sudah selesai.

---

## Checklist

- [x] Membuat Pydantic schemas
- [x] Membuat endpoint Trigger Scraping
- [x] Membuat endpoint Get Video
- [x] Membuat endpoint Get Comments
- [x] Membuat endpoint Search Comments
- [x] Membuat endpoint Get Job Status
- [x] Register semua router di main.py
- [x] Verifikasi di Swagger UI

---

## 4.1 Membuat Pydantic Schemas

Schemas digunakan untuk validasi request/response.

```python
# backend/app/schemas/video.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ScrapeRequest(BaseModel):
    url: str


class VideoResponse(BaseModel):
    id: UUID
    tiktok_video_id: str
    url: str
    author_username: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

```python
# backend/app/schemas/comment.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CommentResponse(BaseModel):
    id: UUID
    comment_id: str
    video_id: UUID
    username: str | None
    display_name: str | None
    comment_text: str
    likes_count: int
    reply_count: int
    comment_created_at: datetime | None
    scraped_at: datetime

    class Config:
        from_attributes = True
```

```python
# backend/app/schemas/job.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class JobResponse(BaseModel):
    id: UUID
    video_id: UUID
    status: str
    total_comments: int
    started_at: datetime
    finished_at: datetime | None

    class Config:
        from_attributes = True


class ScrapeStartResponse(BaseModel):
    job_id: UUID
    status: str
```

```python
# backend/app/schemas/common.py
from pydantic import BaseModel
from typing import Any


class ApiResponse(BaseModel):
    success: bool
    data: Any = None
    message: str | None = None
```

---

## 4.2 Endpoint: Trigger Scraping

```http
POST /api/videos/scrape
```

```python
# backend/app/api/videos.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.schemas.video import ScrapeRequest, VideoResponse
from app.schemas.job import ScrapeStartResponse
from app.schemas.common import ApiResponse
from app.services.video_service import VideoService
from app.services.scraper_service import ScraperService
from app.services.comment_service import CommentService
from app.models.scrape_job import ScrapeJob
from datetime import datetime
import logging

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/videos", tags=["Videos"])


async def run_scraping(video_id, video_url, job_id, db: AsyncSession):
    """Background task untuk menjalankan scraping."""
    from sqlalchemy import select

    try:
        # Update job status ke RUNNING
        stmt = select(ScrapeJob).where(ScrapeJob.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one()
        job.status = "RUNNING"
        await db.commit()

        # Jalankan scraping
        scraper = ScraperService()
        comments_data = await scraper.get_video_comments(video_url)

        # Simpan komentar
        comment_service = CommentService(db)
        saved_count = await comment_service.save_comments(video_id, comments_data)

        # Update job ke SUCCESS
        job.status = "SUCCESS"
        job.total_comments = saved_count
        job.finished_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Scraping selesai untuk job {job_id}: {saved_count} komentar")

    except Exception as e:
        # Update job ke FAILED
        job.status = "FAILED"
        job.finished_at = datetime.utcnow()
        await db.commit()
        logger.error(f"Scraping gagal untuk job {job_id}: {str(e)}")


@router.post("/scrape", response_model=ApiResponse)
async def trigger_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger proses scraping komentar dari video TikTok."""

    # Extract video ID dari URL
    video_id_str = request.url.strip("/").split("/")[-1]

    # Get or create video
    video_service = VideoService(db)
    video = await video_service.get_or_create_video(
        tiktok_video_id=video_id_str,
        url=request.url,
    )

    # Buat scrape job
    job = ScrapeJob(video_id=video.id, status="PENDING")
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Jalankan scraping di background
    background_tasks.add_task(run_scraping, video.id, request.url, job.id, db)

    return ApiResponse(
        success=True,
        data=ScrapeStartResponse(job_id=job.id, status="RUNNING").model_dump(),
    )


@router.get("/{video_id}", response_model=ApiResponse)
async def get_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Ambil detail video berdasarkan ID."""
    from uuid import UUID

    video_service = VideoService(db)
    video = await video_service.get_video_by_id(UUID(video_id))

    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")

    return ApiResponse(
        success=True,
        data=VideoResponse.from_orm(video).model_dump(),
    )
```

---

## 4.3 Endpoint: Comments

```http
GET /api/comments?page=1&limit=100&video_id={video_id}
GET /api/comments/search?q=keyword
```

```python
# backend/app/api/comments.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database.connection import get_db
from app.schemas.comment import CommentResponse
from app.schemas.common import ApiResponse
from app.services.comment_service import CommentService

router = APIRouter(prefix="/api/comments", tags=["Comments"])


@router.get("", response_model=ApiResponse)
async def get_comments(
    video_id: UUID = Query(..., description="ID video"),
    page: int = Query(1, ge=1, description="Halaman"),
    limit: int = Query(100, ge=1, le=500, description="Jumlah per halaman"),
    db: AsyncSession = Depends(get_db),
):
    """Ambil daftar komentar berdasarkan video ID."""
    comment_service = CommentService(db)
    comments = await comment_service.get_comments_by_video(video_id, page, limit)

    return ApiResponse(
        success=True,
        data=[CommentResponse.from_orm(c).model_dump() for c in comments],
    )


@router.get("/search", response_model=ApiResponse)
async def search_comments(
    q: str = Query(..., min_length=1, description="Keyword pencarian"),
    limit: int = Query(100, ge=1, le=500, description="Maksimum hasil"),
    db: AsyncSession = Depends(get_db),
):
    """Cari komentar berdasarkan keyword."""
    comment_service = CommentService(db)
    comments = await comment_service.search_comments(q, limit)

    return ApiResponse(
        success=True,
        data=[CommentResponse.from_orm(c).model_dump() for c in comments],
    )
```

---

## 4.4 Endpoint: Jobs

```http
GET /api/jobs/{job_id}
```

```python
# backend/app/api/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database.connection import get_db
from app.schemas.job import JobResponse
from app.schemas.common import ApiResponse
from app.models.scrape_job import ScrapeJob

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=ApiResponse)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Ambil status scraping job."""
    stmt = select(ScrapeJob).where(ScrapeJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return ApiResponse(
        success=True,
        data=JobResponse.from_orm(job).model_dump(),
    )
```

---

## 4.5 Register Router di main.py

```python
# backend/app/main.py
from fastapi import FastAPI
from app.api.videos import router as video_router
from app.api.comments import router as comment_router
from app.api.jobs import router as job_router

app = FastAPI(
    title="TikTok Scraper API",
    description="API untuk scraping komentar TikTok",
    version="1.0.0",
)

# Register routers
app.include_router(video_router)
app.include_router(comment_router)
app.include_router(job_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

---

## 4.6 Ringkasan Semua Endpoint

| Method | Endpoint                  | Deskripsi                      |
| ------ | ------------------------- | ------------------------------ |
| POST   | `/api/videos/scrape`      | Trigger scraping komentar      |
| GET    | `/api/videos/{video_id}`  | Ambil detail video             |
| GET    | `/api/comments`           | Ambil komentar (+ pagination)  |
| GET    | `/api/comments/search`    | Cari komentar berdasarkan keyword |
| GET    | `/api/jobs/{job_id}`      | Cek status scraping job        |
| GET    | `/health`                 | Health check                   |

---

## Verifikasi Step 4

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Semua endpoint bisa diakses via Swagger UI (`/docs`)
- [ ] `POST /api/videos/scrape` mengembalikan `job_id`
- [ ] `GET /api/videos/{id}` mengembalikan data video
- [ ] `GET /api/comments?video_id=...` mengembalikan komentar
- [ ] `GET /api/comments/search?q=...` bisa mencari komentar
- [ ] `GET /api/jobs/{id}` mengembalikan status job
- [ ] Response mengikuti format standar `{ success, data, message }`

---

> **Selanjutnya:** Lanjut ke [05-error-handling-logging.md](./05-error-handling-logging.md)
