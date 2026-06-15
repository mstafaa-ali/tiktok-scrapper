from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger("api")


class AppException(Exception):
    """Base exception untuk aplikasi."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Resource tidak ditemukan."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class ScrapingException(AppException):
    """Error saat proses scraping."""
    def __init__(self, message: str = "Scraping failed"):
        super().__init__(message=message, status_code=500)


async def app_exception_handler(request: Request, exc: AppException):
    """Handler untuk AppException."""
    logger.error(f"AppException: {exc.message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler untuk validation errors."""
    errors = exc.errors()
    message = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in errors])
    logger.warning(f"Validation Error: {message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": f"Validation Error: {message}"},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handler untuk unhandled exceptions."""
    logger.critical(f"Unhandled Exception: {str(exc)} | Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"},
    )
