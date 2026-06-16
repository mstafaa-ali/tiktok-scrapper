# Step 3 - Scraper Integration

> Panduan integrasi TikTokApi untuk mengambil komentar dari video TikTok.

**Prasyarat:** Pastikan Step 2 (Database Models) sudah selesai.

---

## Checklist

- [x] Install TikTokApi
- [x] Membuat Scraper Service
- [x] Membuat Comment Service
- [x] Membuat Video Service
- [x] Menghubungkan service dengan database
- [x] Testing scraping secara manual

---

## 3.1 Install TikTokApi

```bash
pip install TikTokApi
```

> **Catatan:** TikTokApi mungkin memerlukan Playwright. Jika diperlukan:
>
> ```bash
> pip install playwright
> python -m playwright install
> ```

---

## 3.2 Membuat Scraper Service

Scraper service bertanggung jawab untuk:
- Mengambil komentar dari TikTok
- Mengubah data mentah menjadi format internal

```python
# backend/app/services/scraper_service.py
from TikTokApi import TikTokApi
import logging

logger = logging.getLogger("scraper")


class ScraperService:
    """
    Service untuk mengambil data dari TikTok.
    Hanya bertanggung jawab untuk fetching data, BUKAN menyimpan ke database.
    """

    async def get_video_comments(self, video_url: str) -> list[dict]:
        """
        Mengambil komentar dari video TikTok.

        Args:
            video_url: URL video TikTok

        Returns:
            List of comment dictionaries
        """
        comments = []

        try:
            async with TikTokApi() as api:
                # Extract video ID dari URL
                video_id = self._extract_video_id(video_url)

                video = api.video(id=video_id)

                async for comment in video.comments(count=100):
                    comments.append(self._transform_comment(comment))

            logger.info(f"Berhasil mengambil {len(comments)} komentar dari {video_url}")

        except Exception as e:
            logger.error(f"Gagal mengambil komentar dari {video_url}: {str(e)}")
            raise

        return comments

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID dari URL TikTok."""
        # Contoh URL: https://www.tiktok.com/@user/video/1234567890
        parts = url.strip("/").split("/")
        return parts[-1]

    def _transform_comment(self, raw_comment) -> dict:
        """Transformasi data komentar mentah ke format internal."""
        return {
            "comment_id": str(raw_comment.id),
            "username": raw_comment.author.username if raw_comment.author else None,
            "display_name": raw_comment.author.nickname if raw_comment.author else None,
            "comment_text": raw_comment.text,
            "likes_count": raw_comment.likes_count if hasattr(raw_comment, "likes_count") else 0,
            "reply_count": raw_comment.reply_count if hasattr(raw_comment, "reply_count") else 0,
            "comment_created_at": raw_comment.create_time if hasattr(raw_comment, "create_time") else None,
        }
```

### Input/Output Scraper Service

**Input:**

```python
video_url = "https://www.tiktok.com/@user/video/1234567890"
```

**Output:**

```python
[
    {
        "comment_id": "...",
        "username": "...",
        "display_name": "...",
        "comment_text": "...",
        "likes_count": 10,
        "reply_count": 2,
        "comment_created_at": "..."
    }
]
```

---

## 3.3 Membuat Video Service

Video service bertanggung jawab untuk:
- Menyimpan metadata video
- Mengambil data video
- Mengelola riwayat scraping

```python
# backend/app/services/video_service.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.video import Video
import logging

logger = logging.getLogger("api")


class VideoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_video(self, tiktok_video_id: str, url: str, author_username: str = None, description: str = None) -> Video:
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
        return result.scalars().all()
```

---

## 3.4 Membuat Comment Service

Comment service bertanggung jawab untuk:
- Menyimpan komentar ke database
- Mengambil komentar
- Melakukan pencarian komentar
- Mengelola validasi data

```python
# backend/app/services/comment_service.py
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

    async def get_comments_by_video(self, video_id: UUID, page: int = 1, limit: int = 100) -> list[Comment]:
        """Ambil komentar berdasarkan video ID dengan pagination."""
        offset = (page - 1) * limit
        stmt = (
            select(Comment)
            .where(Comment.video_id == video_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def search_comments(self, keyword: str, limit: int = 100) -> list[Comment]:
        """Cari komentar berdasarkan keyword."""
        stmt = (
            select(Comment)
            .where(Comment.comment_text.ilike(f"%{keyword}%"))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
```

---

## 3.5 Alur Kerja Scraping

Berikut alur lengkap saat proses scraping dijalankan:

```text
1. User mengirim URL video TikTok
       ↓
2. VideoService → get_or_create_video()
       ↓
3. ScrapeJob dibuat dengan status PENDING → RUNNING
       ↓
4. ScraperService → get_video_comments()
       ↓
5. CommentService → save_comments()
       ↓
6. ScrapeJob diupdate → SUCCESS / FAILED
```

---

## 3.6 Testing Manual

Setelah semua service dibuat, test secara manual:

```python
# Contoh penggunaan (bisa dijalankan di script test terpisah)
import asyncio
from app.services.scraper_service import ScraperService

async def test_scraper():
    scraper = ScraperService()
    comments = await scraper.get_video_comments("https://www.tiktok.com/@user/video/123456")
    print(f"Total komentar: {len(comments)}")
    for c in comments[:5]:
        print(f"  - {c['username']}: {c['comment_text'][:50]}")

asyncio.run(test_scraper())
```

---

## Verifikasi Step 3

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] `ScraperService` bisa mengambil komentar dari TikTok
- [ ] `VideoService` bisa get/create video di database
- [ ] `CommentService` bisa menyimpan dan mengambil komentar
- [ ] Komentar duplikat tidak disimpan ulang
- [ ] Log tercatat dengan benar

---

> **Selanjutnya:** Lanjut ke [04-api-development.md](./04-api-development.md)
