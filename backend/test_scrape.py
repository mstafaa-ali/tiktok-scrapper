"""
Script untuk test manual scraping komentar TikTok.
  Jalankan dengan: venv\Scripts\python test_scrape.py <URL_VIDEO>

Contoh:
  venv\Scripts\python test_scrape.py https://www.tiktok.com/@username/video/1234567890
"""
import asyncio
import sys
import os

# Tambahkan root dir ke sys.path agar import app.* bisa berjalan
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.scraper_service import ScraperService
from app.services.video_service import VideoService
from app.services.comment_service import CommentService
from app.models.scrape_job import ScrapeJob
from datetime import datetime, timezone


async def test_scrape(video_url: str):
    """Test full scraping pipeline: fetch → save video → save comments."""
    
    # Setup database session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print(f"\n[1] Memulai scraping untuk URL: {video_url}")

        # Extract video ID
        scraper = ScraperService()
        video_id_str = scraper._extract_video_id(video_url)
        print(f"    Video ID: {video_id_str}")

        # Get or create video record
        video_service = VideoService(db)
        video = await video_service.get_or_create_video(
            tiktok_video_id=video_id_str,
            url=video_url,
        )
        print(f"    Video record ID di DB: {video.id}")

        # Create scrape job
        job = ScrapeJob(video_id=video.id, status="RUNNING")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        print(f"    ScrapeJob ID: {job.id} | Status: {job.status}")

        # Scraping komentar
        print(f"\n[2] Mengambil komentar dari TikTok...")
        try:
            comments_data = await scraper.get_video_comments(video_url, count=200)
            print(f"    Total komentar berhasil diambil: {len(comments_data)}")

            # Preview 3 komentar pertama
            for i, c in enumerate(comments_data[:3]):
                print(f"    [{i+1}] @{c['username']}: {c['comment_text'][:60]}")

            # Simpan komentar ke database
            print(f"\n[3] Menyimpan komentar ke database...")
            comment_service = CommentService(db)
            saved_count = await comment_service.save_comments(video.id, comments_data)
            print(f"    Komentar baru tersimpan: {saved_count}")

            # Update job ke SUCCESS
            job.status = "SUCCESS"
            job.total_comments = saved_count
            job.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await db.commit()
            print(f"    ScrapeJob status: {job.status}")

        except Exception as e:
            # Update job ke FAILED
            job.status = "FAILED"
            job.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await db.commit()
            print(f"    GAGAL: {e}")
            raise

    await engine.dispose()
    print(f"\n[✓] Test selesai!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: venv\\Scripts\\python test_scrape.py <URL_VIDEO_TIKTOK>")
        print("Contoh: venv\\Scripts\\python test_scrape.py https://www.tiktok.com/@youdontknowme._..k/video/7650681134845578510?is_from_webapp=1&sender_device=pc")
        sys.exit(1)

    url = sys.argv[1]
    asyncio.run(test_scrape(url))
