from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.comment import Comment
import logging

logger = logging.getLogger("api")


class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_comments(self, video_id: UUID, comments_data: list[dict]) -> int:
        """
        Simpan daftar komentar ke database.
        Skip komentar yang sudah ada (berdasarkan comment_id).

        Returns:
            Jumlah komentar baru yang berhasil disimpan.
        """
        saved_count = 0

        for data in comments_data:
            # Cek apakah komentar sudah ada
            stmt = select(Comment).where(Comment.comment_id == data["comment_id"])
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing is None:
                comment = Comment(
                    comment_id=data["comment_id"],
                    video_id=video_id,
                    username=data.get("username"),
                    display_name=data.get("display_name"),
                    comment_text=data["comment_text"],
                    likes_count=data.get("likes_count", 0),
                    reply_count=data.get("reply_count", 0),
                    comment_created_at=data.get("comment_created_at"),
                )
                self.db.add(comment)
                saved_count += 1

        await self.db.commit()
        logger.info(f"Berhasil menyimpan {saved_count} komentar baru untuk video {video_id}")
        return saved_count

    async def get_comments_by_video(
        self, video_id: UUID | None, page: int = 1, limit: int = 100
    ) -> list[Comment]:
        """Ambil komentar berdasarkan video ID (opsional) dengan pagination."""
        offset = (page - 1) * limit
        stmt = select(Comment)
        if video_id:
            stmt = stmt.where(Comment.video_id == video_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all_comments(self, video_id: UUID | None = None) -> list[Comment]:
        """Ambil semua komentar (opsional berdasarkan video ID) untuk keperluan export."""
        stmt = select(Comment)
        if video_id:
            stmt = stmt.where(Comment.video_id == video_id)
        # Order by created_at desc
        stmt = stmt.order_by(Comment.comment_created_at.desc().nulls_last())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search_comments(self, keyword: str, limit: int = 100) -> list[Comment]:
        """Cari komentar berdasarkan keyword."""
        stmt = (
            select(Comment)
            .where(Comment.comment_text.ilike(f"%{keyword}%"))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
