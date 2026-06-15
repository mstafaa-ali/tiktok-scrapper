from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CommentResponse(BaseModel):
    id: UUID
    comment_id: str
    video_id: UUID
    username: str | None = None
    display_name: str | None = None
    comment_text: str
    likes_count: int
    reply_count: int
    comment_created_at: datetime | None = None
    scraped_at: datetime

    model_config = {"from_attributes": True}
