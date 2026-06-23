from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tiktok_scraper"
    
    # Scraper configurations
    PROXY_URL: str | None = None
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 5
    SCRAPING_CONCURRENCY: int = 1
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
