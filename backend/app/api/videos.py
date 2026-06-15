from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
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


async def run_scraping(video_id: UUID, video_url: str, job_id: UUID, db: AsyncSession):
    """Background task untuk menjalankan scraping."""
    job = None
    try:
        stmt = select(ScrapeJob).where(ScrapeJob.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one()
        job.status = "RUNNING"
        await db.commit()

        scraper = ScraperService()
        comments_data = await scraper.get_video_comments(video_url)

        comment_service = CommentService(db)
        saved_count = await comment_service.save_comments(video_id, comments_data)

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
        logger.error(f"Scraping gagal untuk job {job_id}: {str(e)}")


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

    job = ScrapeJob(video_id=video.id, status="PENDING")
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(run_scraping, video.id, request.url, job.id, db)

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
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Ambil semua video dengan pagination."""
    video_service = VideoService(db)
    videos = await video_service.get_all_videos(skip=skip, limit=limit)

    return ApiResponse(
        success=True,
        data=[VideoResponse.model_validate(v).model_dump() for v in videos],
    )
