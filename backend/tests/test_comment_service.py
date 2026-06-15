import pytest
from app.services.video_service import VideoService
from app.services.comment_service import CommentService


class TestCommentService:

    async def _create_test_video(self, db_session):
        """Helper: buat video test."""
        service = VideoService(db_session)
        return await service.get_or_create_video(
            tiktok_video_id="test_video",
            url="https://www.tiktok.com/@user/video/test_video",
        )

    async def test_save_comments(self, db_session):
        """Test menyimpan komentar."""
        video = await self._create_test_video(db_session)
        service = CommentService(db_session)

        comments_data = [
            {"comment_id": "c1", "comment_text": "Komentar pertama", "username": "user1"},
            {"comment_id": "c2", "comment_text": "Komentar kedua", "username": "user2"},
        ]

        count = await service.save_comments(video.id, comments_data)
        assert count == 2

    async def test_skip_duplicate_comments(self, db_session):
        """Test komentar duplikat tidak disimpan ulang."""
        video = await self._create_test_video(db_session)
        service = CommentService(db_session)

        comments_data = [
            {"comment_id": "c1", "comment_text": "Komentar pertama", "username": "user1"},
        ]

        # Simpan pertama kali
        count1 = await service.save_comments(video.id, comments_data)
        assert count1 == 1

        # Simpan lagi (harus skip)
        count2 = await service.save_comments(video.id, comments_data)
        assert count2 == 0

    async def test_get_comments_by_video(self, db_session):
        """Test mengambil komentar berdasarkan video."""
        video = await self._create_test_video(db_session)
        service = CommentService(db_session)

        comments_data = [
            {"comment_id": "c1", "comment_text": "Hello", "username": "user1"},
            {"comment_id": "c2", "comment_text": "World", "username": "user2"},
        ]
        await service.save_comments(video.id, comments_data)

        comments = await service.get_comments_by_video(video.id)
        assert len(comments) == 2

    async def test_search_comments(self, db_session):
        """Test pencarian komentar."""
        video = await self._create_test_video(db_session)
        service = CommentService(db_session)

        comments_data = [
            {"comment_id": "c1", "comment_text": "Saya suka video ini", "username": "user1"},
            {"comment_id": "c2", "comment_text": "Biasa saja", "username": "user2"},
            {"comment_id": "c3", "comment_text": "Video yang sangat bagus", "username": "user3"},
        ]
        await service.save_comments(video.id, comments_data)

        results = await service.search_comments("video")
        assert len(results) == 2  # "Saya suka video ini" dan "Video yang sangat bagus"
