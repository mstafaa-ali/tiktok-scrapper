from TikTokApi import TikTokApi
import logging

logger = logging.getLogger("scraper")


class ScraperService:
    """
    Service untuk mengambil data komentar dari TikTok.
    Hanya bertanggung jawab untuk fetching data, BUKAN menyimpan ke database.
    """

    async def get_video_comments(self, video_url: str, count: int = 100) -> list[dict]:
        """
        Mengambil komentar dari video TikTok.

        Args:
            video_url: URL video TikTok
            count: Jumlah komentar yang diambil

        Returns:
            List of comment dictionaries
        """
        comments = []

        try:
            logger.info(f"Mulai scraping komentar dari: {video_url}")

            async with TikTokApi() as api:
                await api.create_sessions(
                    ms_tokens=None,
                    num_sessions=1,
                    sleep_after=3,
                    headless=True,
                )

                video_id = self._extract_video_id(video_url)
                video = api.video(id=video_id, url=video_url)

                async for comment in video.comments(count=count):
                    comments.append(self._transform_comment(comment))

            logger.info(f"Berhasil mengambil {len(comments)} komentar dari {video_url}")

        except Exception as e:
            logger.error(f"Gagal mengambil komentar dari {video_url}: {str(e)}")
            raise

        return comments

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID dari URL TikTok."""
        # Handle URL formats:
        # https://www.tiktok.com/@user/video/1234567890
        # https://vm.tiktok.com/XXXXX/
        parts = url.strip("/").split("/")
        for i, part in enumerate(parts):
            if part == "video" and i + 1 < len(parts):
                return parts[i + 1].split("?")[0]
        # fallback: ambil bagian terakhir
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
