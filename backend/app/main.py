from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

from app.api.videos import router as video_router
from app.api.comments import router as comment_router
from app.api.jobs import router as job_router
from app.core.logging_config import setup_logging
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# Setup logging saat startup
setup_logging()

app = FastAPI(
    title="TikTok Scraper API",
    description="API untuk scraping komentar TikTok",
    version="1.0.0",
)

# Register routers
app.include_router(video_router)
app.include_router(comment_router)
app.include_router(job_router)


# Global exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
