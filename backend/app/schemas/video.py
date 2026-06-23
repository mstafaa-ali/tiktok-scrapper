from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ScrapeRequest(BaseModel):
    url: str
    max_comments: int = 100


class VideoResponse(BaseModel):
    id: UUID
    tiktok_video_id: str
    url: str
    author_username: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    comment_count: int = 0

    model_config = {"from_attributes": True}
