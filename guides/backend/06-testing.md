# Step 6 - Testing

> Panduan implementasi testing untuk memastikan kualitas kode.

**Prasyarat:** Pastikan Step 5 (Error Handling & Logging) sudah selesai.

---

## Checklist

- [ ] Setup testing framework
- [ ] Membuat unit tests
- [ ] Membuat integration tests
- [ ] Membuat load tests
- [ ] Menjalankan semua tests

---

## 6.1 Setup Testing Framework

### Install Dependencies

```bash
pip install pytest pytest-asyncio httpx
```

- `pytest` — Test runner utama
- `pytest-asyncio` — Support untuk async test
- `httpx` — HTTP client untuk testing FastAPI

### Konfigurasi Pytest

```ini
# backend/pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

### Struktur Folder Tests

```text
backend/
└── tests/
    ├── __init__.py
    ├── conftest.py          ← Fixtures dan setup
    ├── test_video_service.py
    ├── test_comment_service.py
    ├── test_scraper_service.py
    ├── test_api_videos.py
    ├── test_api_comments.py
    └── test_api_jobs.py
```

---

## 6.2 Setup Test Database

```python
# backend/tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.connection import Base, get_db

# Gunakan database terpisah untuk testing
TEST_DATABASE_URL = "postgresql+asyncpg://scraper_user:your_password@localhost:5432/tiktok_scraper_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSession = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database():
    """Buat dan bersihkan database untuk setiap test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Provide test database session."""
    async with TestSession() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Provide test HTTP client."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

---

## 6.3 Unit Tests

### Test Video Service

```python
# backend/tests/test_video_service.py
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
```

### Test Comment Service

```python
# backend/tests/test_comment_service.py
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
```

---

## 6.4 Integration Tests (API)

### Test API Videos

```python
# backend/tests/test_api_videos.py
import pytest


class TestVideoAPI:

    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_trigger_scrape(self, client):
        """Test trigger scraping endpoint."""
        response = await client.post(
            "/api/videos/scrape",
            json={"url": "https://www.tiktok.com/@user/video/123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "job_id" in data["data"]
        assert data["data"]["status"] == "RUNNING"

    async def test_get_nonexistent_video(self, client):
        """Test get video yang tidak ada."""
        from uuid import uuid4
        response = await client.get(f"/api/videos/{uuid4()}")
        assert response.status_code == 404

    async def test_trigger_scrape_invalid_url(self, client):
        """Test trigger scraping dengan data invalid."""
        response = await client.post(
            "/api/videos/scrape",
            json={},  # Missing url field
        )
        assert response.status_code == 422
```

### Test API Comments

```python
# backend/tests/test_api_comments.py
import pytest


class TestCommentAPI:

    async def test_search_comments_empty(self, client):
        """Test pencarian komentar kosong."""
        response = await client.get("/api/comments/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []

    async def test_search_without_query(self, client):
        """Test pencarian tanpa query parameter."""
        response = await client.get("/api/comments/search")
        assert response.status_code == 422  # Validation error
```

---

## 6.5 Load Testing (Opsional)

### Install Locust

```bash
pip install locust
```

### Buat Load Test File

```python
# backend/tests/locustfile.py
from locust import HttpUser, task, between


class TikTokScraperUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(1)
    def search_comments(self):
        self.client.get("/api/comments/search?q=test")
```

### Jalankan Load Test

```bash
locust -f tests/locustfile.py --host=http://localhost:8000
```

Buka `http://localhost:8089` untuk melihat dashboard Locust.

---

## 6.6 Menjalankan Tests

### Jalankan semua tests

```bash
cd backend
pytest -v
```

### Jalankan test tertentu

```bash
pytest tests/test_video_service.py -v
pytest tests/test_api_videos.py -v
```

### Jalankan dengan coverage

```bash
pip install pytest-cov
pytest --cov=app --cov-report=html -v
```

Hasil coverage bisa dilihat di `htmlcov/index.html`.

---

## Verifikasi Step 6

Pastikan semua test lulus:

- [ ] Semua unit tests PASS
- [ ] Semua integration tests PASS
- [ ] Coverage minimal 70%
- [ ] Load test berjalan tanpa error fatal

---

## 🎉 Selesai!

Selamat, kamu sudah menyelesaikan semua step pengerjaan backend TikTok Scraper!

### Ringkasan yang sudah dikerjakan:

| Step | Nama                     | Status |
| ---- | ------------------------ | ------ |
| 0    | Overview & Arsitektur    | ✅     |
| 1    | Project Setup            | ✅     |
| 2    | Database Models          | ✅     |
| 3    | Scraper Integration      | ✅     |
| 4    | API Development          | ✅     |
| 5    | Error Handling & Logging | ✅     |
| 6    | Testing                  | ✅     |
