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
        data=JobResponse.model_validate(job).model_dump(),
    )
