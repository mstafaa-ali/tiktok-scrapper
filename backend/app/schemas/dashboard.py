from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class DashboardStats(BaseModel):
    total_videos: int
    total_comments: int
    total_jobs: int
    success_rate: float

class RecentActivity(BaseModel):
    id: str
    type: Literal["scrape", "video_added", "comments_added"]
    description: str
    timestamp: datetime
