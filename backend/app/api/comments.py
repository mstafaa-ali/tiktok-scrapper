from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from fastapi.responses import StreamingResponse
import io
import csv
import openpyxl
from app.database.connection import get_db
from app.schemas.comment import CommentResponse
from app.schemas.common import ApiResponse
from app.services.comment_service import CommentService

router = APIRouter(prefix="/api/comments", tags=["Comments"])


@router.get("", response_model=ApiResponse)
async def get_comments(
    video_id: UUID | None = Query(None, description="ID video"),
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


@router.get("/export")
async def export_comments(
    video_id: UUID | None = Query(None, description="ID video"),
    format: str = Query("csv", description="Format export: csv atau excel"),
    db: AsyncSession = Depends(get_db),
):
    """Export komentar menjadi CSV atau Excel."""
    comment_service = CommentService(db)
    comments = await comment_service.get_all_comments(video_id)

    if format.lower() == "excel":
        output = io.BytesIO()
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Comments"

        # Header
        sheet.append([
            "Comment ID", "Video ID", "Username", "Display Name",
            "Comment Text", "Likes", "Replies", "Created At"
        ])

        # Baris data
        for c in comments:
            sheet.append([
                c.comment_id,
                str(c.video_id),
                c.username,
                c.display_name,
                c.comment_text,
                c.likes_count,
                c.reply_count,
                c.comment_created_at.isoformat() if c.comment_created_at else ""
            ])

        workbook.save(output)
        output.seek(0)
        
        filename = f"comments_export_{video_id}.xlsx" if video_id else "comments_export_all.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        # Buat CSV di memori
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Comment ID", "Video ID", "Username", "Display Name",
            "Comment Text", "Likes", "Replies", "Created At"
        ])

        # Baris data
        for c in comments:
            writer.writerow([
                c.comment_id,
                str(c.video_id),
                c.username,
                c.display_name,
                c.comment_text,
                c.likes_count,
                c.reply_count,
                c.comment_created_at.isoformat() if c.comment_created_at else ""
            ])

        output.seek(0)

        filename = f"comments_export_{video_id}.csv" if video_id else "comments_export_all.csv"

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
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
