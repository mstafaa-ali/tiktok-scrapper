from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from sqlalchemy import select

from app.database.connection import get_db
from app.schemas.video import ScrapeRequest, VideoResponse
from app.schemas.job import ScrapeStartResponse
from app.schemas.common import ApiResponse
from app.services.video_service import VideoService
from app.services.scraper_service import ScraperService
from app.services.comment_service import CommentService
from app.models.scrape_job import ScrapeJob
import logging

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/videos", tags=["Videos"])


async def run_scraping(video_id: UUID, video_url: str, job_id: UUID, max_comments: int = 100):
    """Background task untuk menjalankan scraping."""
    import asyncio
    import concurrent.futures
    from app.database.connection import async_session
    from app.services.scraper_service import sync_get_video_comments
    from app.core.config import settings

    # Gunakan session DB yang baru untuk task background ini
    async with async_session() as db:
        job = None
        try:
            stmt = select(ScrapeJob).where(ScrapeJob.id == job_id)
            result = await db.execute(stmt)
            job = result.scalar_one()
            job.status = "RUNNING"
            await db.commit()

            # Jalankan scraper di proses terpisah untuk menghindari konflik Playwright dengan event loop Uvicorn
            loop = asyncio.get_running_loop()
            with concurrent.futures.ProcessPoolExecutor(max_workers=settings.SCRAPING_CONCURRENCY) as pool:
                saved_count = await loop.run_in_executor(
                    pool, sync_get_video_comments, video_url, str(video_id), max_comments
                )

            # Penyimpanan dilakukan secara incremental oleh child process,
            # sync_get_video_comments langsung me-return total komentar yang berhasil di-scrape.

            job.status = "SUCCESS"
            job.total_comments = saved_count
            job.finished_at = datetime.utcnow()
            await db.commit()

            logger.info(f"Scraping selesai untuk job {job_id}: {saved_count} komentar")

        except Exception as e:
            if job:
                job.status = "FAILED"
                job.finished_at = datetime.utcnow()
                await db.commit()
            logger.error(f"Scraping gagal untuk job {job_id}: {type(e).__name__}: {e}", exc_info=True)


@router.post("/scrape", response_model=ApiResponse)
async def trigger_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger proses scraping komentar dari video TikTok."""
    scraper = ScraperService()
    video_id_str = scraper._extract_video_id(request.url)

    video_service = VideoService(db)
    video = await video_service.get_or_create_video(
        tiktok_video_id=video_id_str,
        url=request.url,
    )

    job = ScrapeJob(video_id=video.id, status="PENDING", target_comments=request.max_comments)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(run_scraping, video.id, request.url, job.id, request.max_comments)

    return ApiResponse(
        success=True,
        data=ScrapeStartResponse(job_id=job.id, status="RUNNING").model_dump(),
    )


@router.get("/{video_id}", response_model=ApiResponse)
async def get_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Ambil detail video berdasarkan ID."""
    video_service = VideoService(db)
    video = await video_service.get_video_by_id(video_id)

    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")

    return ApiResponse(
        success=True,
        data=VideoResponse.model_validate(video).model_dump(),
    )


@router.get("", response_model=ApiResponse)
async def list_videos(
    page: int = Query(1, ge=1, description="Halaman"),
    page_size: int = Query(20, ge=1, le=100, description="Jumlah per halaman"),
    search: str | None = Query(None, description="Pencarian"),
    sort_by: str = Query("created_at", description="Kolom sorting"),
    sort_order: str = Query("desc", description="Arah sorting"),
    db: AsyncSession = Depends(get_db),
):
    """Ambil semua video dengan pagination."""
    video_service = VideoService(db)
    skip = (page - 1) * page_size
    videos, total = await video_service.get_all_videos(
        skip=skip,
        limit=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    import math
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ApiResponse(
        success=True,
        data={
            "data": [VideoResponse.model_validate(v).model_dump() for v in videos],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )
