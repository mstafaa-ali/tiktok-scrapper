from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database.connection import get_db
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardStats, RecentActivity
from app.models.video import Video
from app.models.comment import Comment
from app.models.scrape_job import ScrapeJob

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=ApiResponse)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # Total Videos
    total_videos_result = await db.execute(select(func.count()).select_from(Video))
    total_videos = total_videos_result.scalar() or 0

    # Total Comments
    total_comments_result = await db.execute(select(func.count()).select_from(Comment))
    total_comments = total_comments_result.scalar() or 0

    # Total Jobs
    total_jobs_result = await db.execute(select(func.count()).select_from(ScrapeJob))
    total_jobs = total_jobs_result.scalar() or 0

    # Success Rate
    success_jobs_result = await db.execute(select(func.count()).select_from(ScrapeJob).where(ScrapeJob.status == "SUCCESS"))
    success_jobs = success_jobs_result.scalar() or 0
    
    success_rate = 0.0
    if total_jobs > 0:
        success_rate = round((success_jobs / total_jobs) * 100, 2)

    return ApiResponse(
        success=True,
        data=DashboardStats(
            total_videos=total_videos,
            total_comments=total_comments,
            total_jobs=total_jobs,
            success_rate=success_rate,
        ).model_dump()
    )

@router.get("/activity", response_model=ApiResponse)
async def get_recent_activity(db: AsyncSession = Depends(get_db)):
    # Fetch latest 5 scrape jobs
    stmt = select(ScrapeJob).order_by(desc(ScrapeJob.started_at)).limit(5)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    activities = []
    for job in jobs:
        if job.status == "SUCCESS":
            act_desc = f"Scraping completed: {job.total_comments} comments"
            activities.append(RecentActivity(id=str(job.id), type="comments_added", description=act_desc, timestamp=job.finished_at or job.created_at))
        elif job.status == "FAILED":
            act_desc = f"Scraping failed"
            activities.append(RecentActivity(id=str(job.id), type="scrape", description=act_desc, timestamp=job.finished_at or job.created_at))
        elif job.status == "RUNNING":
            act_desc = f"Scraping started..."
            activities.append(RecentActivity(id=str(job.id), type="scrape", description=act_desc, timestamp=job.created_at))
        elif job.status == "PENDING":
            act_desc = f"Scraping pending..."
            activities.append(RecentActivity(id=str(job.id), type="scrape", description=act_desc, timestamp=job.created_at))

    return ApiResponse(
        success=True,
        data=[a.model_dump() for a in activities]
    )
