import pytest
from app.services.video_service import VideoService


class TestVideoService:

    async def test_create_new_video(self, db_session):
        """Test membuat video baru."""
        service = VideoService(db_session)
        video = await service.get_or_create_video(
            tiktok_video_id="123456",
            url="https://www.tiktok.com/@user/video/123456",
            author_username="testuser",
        )
        assert video is not None
        assert video.tiktok_video_id == "123456"
        assert video.url == "https://www.tiktok.com/@user/video/123456"

    async def test_get_existing_video(self, db_session):
        """Test mendapatkan video yang sudah ada (tidak duplikat)."""
        service = VideoService(db_session)

        # Buat video pertama
        video1 = await service.get_or_create_video(
            tiktok_video_id="123456",
            url="https://www.tiktok.com/@user/video/123456",
        )

        # Ambil video yang sama
        video2 = await service.get_or_create_video(
            tiktok_video_id="123456",
            url="https://www.tiktok.com/@user/video/123456",
        )

        assert video1.id == video2.id  # Harus ID yang sama

    async def test_get_video_by_id(self, db_session):
        """Test ambil video berdasarkan ID."""
        service = VideoService(db_session)
        video = await service.get_or_create_video(
            tiktok_video_id="123456",
            url="https://www.tiktok.com/@user/video/123456",
        )

        found = await service.get_video_by_id(video.id)
        assert found is not None
        assert found.id == video.id

    async def test_get_nonexistent_video(self, db_session):
        """Test ambil video yang tidak ada."""
        from uuid import uuid4
        service = VideoService(db_session)
        found = await service.get_video_by_id(uuid4())
        assert found is None
