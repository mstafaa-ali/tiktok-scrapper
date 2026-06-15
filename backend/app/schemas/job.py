from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class JobResponse(BaseModel):
    id: UUID
    video_id: UUID
    status: str
    total_comments: int
    started_at: datetime
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}


class ScrapeStartResponse(BaseModel):
    job_id: UUID
    status: str
