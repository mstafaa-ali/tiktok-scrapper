from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.connection import get_db
from app.schemas.comment import CommentResponse
from app.schemas.common import ApiResponse
from app.services.comment_service import CommentService

router = APIRouter(prefix="/api/comments", tags=["Comments"])


@router.get("", response_model=ApiResponse)
async def get_comments(
    video_id: UUID = Query(..., description="ID video"),
    page: int = Query(1, ge=1, description="Halaman"),
    limit: int = Query(100, ge=1, le=500, description="Jumlah per halaman"),
    db: AsyncSession = Depends(get_db),
):
    """Ambil daftar komentar berdasarkan video ID."""
    comment_service = CommentService(db)
    comments = await comment_service.get_comments_by_video(video_id, page, limit)

    return ApiResponse(
        success=True,
        data=[CommentResponse.model_validate(c).model_dump() for c in comments],
    )


@router.get("/search", response_model=ApiResponse)
async def search_comments(
    q: str = Query(..., min_length=1, description="Keyword pencarian"),
    limit: int = Query(100, ge=1, le=500, description="Maksimum hasil"),
    db: AsyncSession = Depends(get_db),
):
    """Cari komentar berdasarkan keyword."""
    comment_service = CommentService(db)
    comments = await comment_service.search_comments(q, limit)

    return ApiResponse(
        success=True,
        data=[CommentResponse.model_validate(c).model_dump() for c in comments],
    )
