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
