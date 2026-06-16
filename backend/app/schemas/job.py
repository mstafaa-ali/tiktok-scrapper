from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class JobResponse(BaseModel):
    id: UUID
    video_id: UUID
    video_url: str | None = None
    status: str
    comments_scraped: int
    error_message: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    data: list[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScrapeStartResponse(BaseModel):
    job_id: UUID
    status: str

