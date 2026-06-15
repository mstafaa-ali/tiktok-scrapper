# Step 5 - Error Handling & Logging

> Panduan implementasi error handling standar dan logging system.

**Prasyarat:** Pastikan Step 4 (API Development) sudah selesai.

---

## Checklist

- [ ] Setup global exception handler
- [ ] Standarisasi response format
- [ ] Setup logging configuration
- [ ] Implementasi logging di setiap layer
- [ ] Buat log files

---

## 5.1 Standar Response Format

Semua API response harus mengikuti format standar ini:

### Success Response

```json
{
  "success": true,
  "data": {}
}
```

### Error Response

```json
{
  "success": false,
  "message": "Video not found"
}
```

---

## 5.2 Global Exception Handler

```python
# backend/app/core/exceptions.py
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
```

### Register Exception Handlers di main.py

```python
# backend/app/main.py (tambahan)
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

---

## 5.3 Logging Configuration

### Setup Logging

```python
# backend/app/core/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging():
    """Setup konfigurasi logging untuk seluruh aplikasi."""

    # Format log
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── API Logger ──
    api_logger = logging.getLogger("api")
    api_logger.setLevel(logging.INFO)

    api_file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "api.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
    )
    api_file_handler.setFormatter(formatter)
    api_logger.addHandler(api_file_handler)

    # ── Scraper Logger ──
    scraper_logger = logging.getLogger("scraper")
    scraper_logger.setLevel(logging.INFO)

    scraper_file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "scraper.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
    )
    scraper_file_handler.setFormatter(formatter)
    scraper_logger.addHandler(scraper_file_handler)

    # ── Console Handler (untuk development) ──
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    api_logger.addHandler(console_handler)
    scraper_logger.addHandler(console_handler)

    api_logger.info("Logging system initialized")
```

### Inisialisasi Logging di main.py

```python
# backend/app/main.py (tambahan)
from app.core.logging_config import setup_logging

# Inisialisasi logging saat startup
setup_logging()
```

---

## 5.4 Log Files

### Struktur Direktori

```text
logs/
├── api.log       ← Log dari API layer
└── scraper.log   ← Log dari scraper service
```

### Data yang Dicatat

| Logger    | Data yang Dicatat                                |
| --------- | ------------------------------------------------ |
| `api`     | Request masuk, response, error API, validation   |
| `scraper` | Proses scraping dimulai/selesai, jumlah komentar, error scraping |

### Format Log

```text
2024-01-15 10:30:45 | INFO     | api     | Request POST /api/videos/scrape
2024-01-15 10:30:46 | INFO     | scraper | Mulai scraping: https://tiktok.com/...
2024-01-15 10:30:50 | INFO     | scraper | Berhasil mengambil 150 komentar
2024-01-15 10:30:50 | ERROR    | scraper | Gagal scraping: Connection timeout
```

---

## 5.5 Penggunaan di Service Layer

Contoh penggunaan logging di service:

```python
import logging

logger = logging.getLogger("scraper")  # atau "api"

# Info
logger.info(f"Mulai scraping video: {video_url}")

# Warning
logger.warning(f"Rate limit hampir tercapai")

# Error
logger.error(f"Gagal scraping: {str(error)}")

# Critical
logger.critical(f"Database connection lost", exc_info=True)
```

---

## Verifikasi Step 5

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Exception handler terdaftar di `main.py`
- [ ] Error response mengikuti format `{ success: false, message: "..." }`
- [ ] File `logs/api.log` terisi saat ada request
- [ ] File `logs/scraper.log` terisi saat scraping berjalan
- [ ] Validation error mengembalikan pesan yang jelas
- [ ] Unhandled exception tidak menampilkan stack trace ke client

---

> **Selanjutnya:** Lanjut ke [06-testing.md](./06-testing.md)
