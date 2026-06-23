from TikTokApi import TikTokApi
import logging
from uuid import UUID
import asyncio

logger = logging.getLogger("scraper")


class ScraperService:
    """
    Service untuk mengambil data komentar dari TikTok.
    Sekarang dilengkapi dengan kapabilitas penyimpanan batch langsung ke DB.
    """
    
    def __init__(self, db_session=None):
        """
        db_session: AsyncSession (opsional). Jika diberikan, scraper akan menyimpan data secara batch.
        """
        from app.core.config import settings
        self.db = db_session
        self.proxy_url = settings.PROXY_URL
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY_SECONDS

    async def get_video_comments(self, video_url: str, video_id: UUID = None, count: int = 100) -> int:
        """
        Mengambil komentar dari video TikTok dan menyimpannya per batch.

        Args:
            video_url: URL video TikTok
            video_id: UUID video di database (wajib untuk save ke DB)
            count: Target jumlah komentar

        Returns:
            Jumlah total komentar yang berhasil disimpan/di-scrape
        """
        total_scraped = 0
        total_saved = 0
        batch_size = 50
        current_batch = []
        last_error = None
        
        # Gunakan cursor tracking jika TikTokApi mendukungnya di masa depan.
        # Saat ini, API secara otomatis melakukan scroll. Kita tangkap seberapa banyak yang bisa didapat.

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Mulai scraping komentar dari: {video_url} (attempt {attempt + 1}/{self.max_retries + 1})")
                
                proxies = [self.proxy_url] if self.proxy_url else None
                if proxies:
                    logger.info("Menggunakan proxy untuk koneksi.")

                async with TikTokApi() as api:
                    await api.create_sessions(
                        ms_tokens=None,
                        num_sessions=1,
                        sleep_after=5,
                        headless=False,
                        timeout=60000,
                        proxies=proxies,
                        suppress_resource_load_types=["image", "media", "font", "stylesheet"],
                    )

                    tiktok_video_id = self._extract_video_id(video_url)
                    video = api.video(id=tiktok_video_id, url=video_url)

                    try:
                        async for comment in video.comments(count=count):
                            current_batch.append(self._transform_comment(comment))
                            total_scraped += 1
                            
                            # Simpan per batch ke DB jika db_session ada
                            if len(current_batch) >= batch_size:
                                if self.db and video_id:
                                    saved = await self._save_batch(video_id, current_batch)
                                    total_saved += saved
                                current_batch = []
                                
                            # Jeda acak (0.5s - 1.5s) untuk hindari rate limit bot detection
                            import random
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                            
                    except Exception as inner_e:
                        logger.warning(f"Terputus saat iterasi di komentar ke-{total_scraped}: {type(inner_e).__name__}: {inner_e}")
                        # Simpan sisa batch sebelum break
                        if self.db and video_id and current_batch:
                            saved = await self._save_batch(video_id, current_batch)
                            total_saved += saved
                            current_batch = []
                            
                        if total_scraped > 0:
                            # Anggap sukses parsial jika sudah dapat sebagian
                            break
                        raise inner_e # Lempar ulang jika belum dapat sama sekali
                
                # Simpan sisa batch terakhir (jika tidak terjadi exception)
                if self.db and video_id and current_batch:
                    saved = await self._save_batch(video_id, current_batch)
                    total_saved += saved
                    current_batch = []

                logger.info(f"Berhasil mengambil total {total_scraped} komentar dari {video_url}")
                return total_saved

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} gagal untuk {video_url}: {type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Menunggu {delay} detik sebelum mencoba lagi...")
                    await asyncio.sleep(delay)
                    # Reset counter dan array jika kita harus mengulang dari awal (karena library tidak support resume)
                    # Namun jika kita sudah menyimpan ke DB di upaya sebelumnya, kita mungkin menduplikasi request.
                    # _save_batch (lewat CommentService) harus menangani upsert/ignore duplikat.
                    current_batch = []

        logger.error(f"Gagal menyelesaikan scraping dari {video_url} setelah {self.max_retries + 1} percobaan: {last_error}")
        return total_saved

    async def _save_batch(self, video_id: UUID, batch: list[dict]) -> int:
        from app.services.comment_service import CommentService
        comment_service = CommentService(self.db)
        saved = await comment_service.save_comments(video_id, batch)
        logger.info(f"Batch tersimpan ke database: {saved} komentar.")
        return saved

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID dari URL TikTok."""
        parts = url.strip("/").split("/")
        for i, part in enumerate(parts):
            if part == "video" and i + 1 < len(parts):
                return parts[i + 1].split("?")[0]
        return parts[-1].split("?")[0]

    def _transform_comment(self, raw_comment) -> dict:
        """Transformasi data komentar mentah ke format internal."""
        return {
            "comment_id": str(raw_comment.id),
            "username": getattr(raw_comment.author, "username", None) if raw_comment.author else None,
            "display_name": getattr(raw_comment.author, "nickname", None) if raw_comment.author else None,
            "comment_text": raw_comment.text or "",
            "likes_count": getattr(raw_comment, "likes_count", 0) or 0,
            "reply_count": getattr(raw_comment, "reply_count", 0) or 0,
            "comment_created_at": getattr(raw_comment, "create_time", None),
        }

def sync_get_video_comments(video_url: str, video_id_str: str, count: int = 100) -> int:
    """
    Wrapper untuk menjalankan scraper di event loop terpisah.
    Diubah agar child process mengelola koneksi DB sendiri dan menyimpan batch secara langsung.
    """
    import asyncio
    import sys
    import logging
    from uuid import UUID
    from app.database.connection import async_session

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | scraper_worker | %(message)s")

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    async def _run():
        video_id = UUID(video_id_str)
        async with async_session() as db:
            scraper = ScraperService(db_session=db)
            return await scraper.get_video_comments(video_url, video_id, count)

    try:
        return asyncio.run(_run())
    except Exception as e:
        raise RuntimeError(f"Scraping error: {type(e).__name__}: {str(e)}")

