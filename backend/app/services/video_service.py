from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.video import Video
import logging

logger = logging.getLogger("api")


class VideoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_video(
        self,
        tiktok_video_id: str,
        url: str,
        author_username: str = None,
        description: str = None,
    ) -> Video:
        """Ambil video yang sudah ada, atau buat baru jika belum ada."""
        stmt = select(Video).where(Video.tiktok_video_id == tiktok_video_id)
        result = await self.db.execute(stmt)
        video = result.scalar_one_or_none()

        if video is None:
            video = Video(
                tiktok_video_id=tiktok_video_id,
                url=url,
                author_username=author_username,
                description=description,
            )
            self.db.add(video)
            await self.db.commit()
            await self.db.refresh(video)
            logger.info(f"Video baru dibuat: {tiktok_video_id}")

        return video

    async def get_video_by_id(self, video_id: UUID) -> Video | None:
        """Ambil video berdasarkan ID."""
        stmt = select(Video).where(Video.id == video_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_videos(self, skip: int = 0, limit: int = 20) -> list[Video]:
        """Ambil semua video dengan pagination."""
        stmt = select(Video).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
