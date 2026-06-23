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

    async def get_all_videos(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[list[dict], int]:
        from sqlalchemy import func, desc, asc, or_
        from app.models.comment import Comment

        # Hitung total
        count_stmt = select(func.count(Video.id))
        if search:
            count_stmt = count_stmt.where(
                or_(
                    Video.description.ilike(f"%{search}%"),
                    Video.author_username.ilike(f"%{search}%")
                )
            )
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # Ambil data
        stmt = select(
            Video,
            func.count(Comment.id).label("comment_count")
        ).outerjoin(
            Comment, Video.id == Comment.video_id
        ).group_by(Video.id)

        if search:
            stmt = stmt.where(
                or_(
                    Video.description.ilike(f"%{search}%"),
                    Video.author_username.ilike(f"%{search}%")
                )
            )

        # Sorting
        sort_col = getattr(Video, sort_by, Video.created_at)
        if sort_order == "desc":
            stmt = stmt.order_by(desc(sort_col))
        else:
            stmt = stmt.order_by(asc(sort_col))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)

        videos = []
        for row in result.all():
            video_obj = row.Video
            video_dict = {
                "id": video_obj.id,
                "tiktok_video_id": video_obj.tiktok_video_id,
                "url": video_obj.url,
                "author_username": video_obj.author_username,
                "description": video_obj.description,
                "created_at": video_obj.created_at,
                "updated_at": video_obj.updated_at,
                "comment_count": row.comment_count
            }
            videos.append(video_dict)

        return videos, total
