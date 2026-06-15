import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging():
    """Setup konfigurasi logging untuk seluruh aplikasi."""

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── API Logger ──
    api_logger = logging.getLogger("api")
    api_logger.setLevel(logging.INFO)
    api_file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "api.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
    )
    api_file_handler.setFormatter(formatter)
    api_logger.addHandler(api_file_handler)

    # ── Scraper Logger ──
    scraper_logger = logging.getLogger("scraper")
    scraper_logger.setLevel(logging.INFO)
    scraper_file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "scraper.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
    )
    scraper_file_handler.setFormatter(formatter)
    scraper_logger.addHandler(scraper_file_handler)

    # ── Console Handler (development) ──
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    api_logger.addHandler(console_handler)
    scraper_logger.addHandler(console_handler)

    api_logger.info("Logging system initialized")
