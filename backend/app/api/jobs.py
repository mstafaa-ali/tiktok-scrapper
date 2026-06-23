from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from sqlalchemy.orm import joinedload
from app.database.connection import get_db
from app.schemas.job import JobResponse, JobListResponse
from app.schemas.common import ApiResponse
from app.models.scrape_job import ScrapeJob

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("", response_model=ApiResponse)
async def get_jobs(
    page: int = 1,
    page_size: int = 5,
    status: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    """Ambil daftar scraping jobs dengan pagination."""
    # Build query
    stmt = select(ScrapeJob).options(joinedload(ScrapeJob.video))
    if status:
        stmt = stmt.where(ScrapeJob.status == status)

    # Order
    order_col = ScrapeJob.started_at
    if sort_order == "desc":
        stmt = stmt.order_by(order_col.desc())
    else:
        stmt = stmt.order_by(order_col.asc())

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # Limit / Offset
    stmt = stmt.limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    # Map responses
    job_responses = []
    for job in jobs:
        job_responses.append(
            JobResponse(
                id=job.id,
                video_id=job.video_id,
                video_url=job.video.url if job.video else None,
                status=job.status,
                target_comments=job.target_comments or 100,
                comments_scraped=job.total_comments,
                error_message=None,
                started_at=job.started_at,
                finished_at=job.finished_at,
                created_at=job.started_at,
            )
        )

    import math
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return ApiResponse(
        success=True,
        data=JobListResponse(
            data=job_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ).model_dump(),
    )


@router.get("/{job_id}", response_model=ApiResponse)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Ambil status scraping job."""
    stmt = select(ScrapeJob).where(ScrapeJob.id == job_id).options(joinedload(ScrapeJob.video))
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job_response = JobResponse(
        id=job.id,
        video_id=job.video_id,
        video_url=job.video.url if job.video else None,
        status=job.status,
        target_comments=job.target_comments or 100,
        comments_scraped=job.total_comments,
        error_message=None,
        started_at=job.started_at,
        finished_at=job.finished_at,
        created_at=job.started_at,
    )

    return ApiResponse(
        success=True,
        data=job_response.model_dump(),
    )
