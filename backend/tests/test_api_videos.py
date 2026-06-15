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
