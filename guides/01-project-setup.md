# Step 1 - Project Setup

> Panduan lengkap untuk menyiapkan seluruh fondasi project.

---

## Checklist

- [x] Setup FastAPI project
- [x] Setup PostgreSQL (Local)
- [x] Setup SQLAlchemy
- [x] Setup Alembic
- [-] Setup Docker (Skipped - using local setup)

---

## 1.1 Setup FastAPI

### Langkah-langkah

1. **Buat folder project**

   ```bash
   mkdir -p backend/app
   cd backend
   ```

2. **Buat virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # atau
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install fastapi uvicorn[standard]
   ```

4. **Buat file `main.py`**

   ```python
   # backend/app/main.py
   from fastapi import FastAPI

   app = FastAPI(
       title="TikTok Scraper API",
       description="API untuk scraping komentar TikTok",
       version="1.0.0"
   )

   @app.get("/health")
   async def health_check():
       return {"status": "ok"}
   ```

5. **Jalankan server**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Verifikasi**
   - Buka `http://localhost:8000/health` → harus return `{"status": "ok"}`
   - Buka `http://localhost:8000/docs` → Swagger UI harus tampil

---

## 1.2 Setup PostgreSQL

### Langkah-langkah

1. **Install PostgreSQL** (jika belum ada)

   - Download dari [postgresql.org](https://www.postgresql.org/download/)
   - Atau gunakan Docker (lihat bagian 1.5)

2. **Buat database**

   ```sql
   CREATE DATABASE tiktok_scraper;
   CREATE USER scraper_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE tiktok_scraper TO scraper_user;
   ```

3. **Catat connection string**

   ```text
   postgresql://scraper_user:your_password@localhost:5432/tiktok_scraper
   ```

---

## 1.3 Setup SQLAlchemy

### Langkah-langkah

1. **Install dependencies**

   ```bash
   pip install sqlalchemy[asyncio] asyncpg
   ```

2. **Buat konfigurasi database**

   ```python
   # backend/app/database/connection.py
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker, DeclarativeBase

   DATABASE_URL = "postgresql+asyncpg://scraper_user:your_password@localhost:5432/tiktok_scraper"

   engine = create_async_engine(DATABASE_URL, echo=True)

   async_session = sessionmaker(
       engine,
       class_=AsyncSession,
       expire_on_commit=False
   )

   class Base(DeclarativeBase):
       pass

   async def get_db():
       async with async_session() as session:
           yield session
   ```

3. **Buat file konfigurasi environment**

   ```python
   # backend/app/core/config.py
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       DATABASE_URL: str = "postgresql+asyncpg://scraper_user:your_password@localhost:5432/tiktok_scraper"
       
       class Config:
           env_file = ".env"

   settings = Settings()
   ```

4. **Install pydantic-settings**

   ```bash
   pip install pydantic-settings
   ```

5. **Buat file `.env`**

   ```env
   DATABASE_URL=postgresql+asyncpg://scraper_user:your_password@localhost:5432/tiktok_scraper
   ```

---

## 1.4 Setup Alembic

### Langkah-langkah

1. **Install Alembic**

   ```bash
   pip install alembic
   ```

2. **Inisialisasi Alembic**

   ```bash
   cd backend
   alembic init app/migrations
   ```

3. **Konfigurasi `alembic.ini`**

   Update `sqlalchemy.url`:

   ```ini
   sqlalchemy.url = postgresql://scraper_user:your_password@localhost:5432/tiktok_scraper
   ```

4. **Update `env.py` di folder migrations**

   ```python
   # backend/app/migrations/env.py
   # Tambahkan import model Base
   from app.database.connection import Base
   target_metadata = Base.metadata
   ```

5. **Verifikasi**

   ```bash
   alembic current  # Harus berjalan tanpa error
   ```

---

## 1.5 Setup Docker (Opsional tapi Direkomendasikan)

### Langkah-langkah

1. **Buat `docker-compose.yml`**

   ```yaml
   # backend/docker-compose.yml
   version: "3.8"

   services:
     db:
       image: postgres:15
       container_name: tiktok_scraper_db
       environment:
         POSTGRES_DB: tiktok_scraper
         POSTGRES_USER: scraper_user
         POSTGRES_PASSWORD: your_password
       ports:
         - "5432:5432"
       volumes:
         - pgdata:/var/lib/postgresql/data

     api:
       build: .
       container_name: tiktok_scraper_api
       ports:
         - "8000:8000"
       depends_on:
         - db
       environment:
         DATABASE_URL: postgresql+asyncpg://scraper_user:your_password@db:5432/tiktok_scraper
       volumes:
         - .:/app

   volumes:
     pgdata:
   ```

2. **Buat `Dockerfile`**

   ```dockerfile
   # backend/Dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Buat `requirements.txt`**

   ```bash
   pip freeze > requirements.txt
   ```

4. **Jalankan**

   ```bash
   docker-compose up -d
   ```

---

## 1.6 Buat Struktur Folder Lengkap

Jalankan perintah berikut untuk membuat seluruh folder yang dibutuhkan:

```bash
mkdir -p backend/app/api
mkdir -p backend/app/services
mkdir -p backend/app/models
mkdir -p backend/app/schemas
mkdir -p backend/app/database
mkdir -p backend/app/core
mkdir -p backend/app/migrations
mkdir -p backend/logs
```

Buat file `__init__.py` di setiap folder:

```bash
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/services/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/database/__init__.py
touch backend/app/core/__init__.py
```

---

## Verifikasi Step 1

Sebelum lanjut ke step berikutnya, pastikan:

- [ ] Server FastAPI berjalan di `http://localhost:8000`
- [ ] Swagger UI bisa diakses di `http://localhost:8000/docs`
- [ ] PostgreSQL database `tiktok_scraper` sudah dibuat
- [ ] Alembic sudah terinisialisasi
- [ ] Seluruh folder project sudah terbuat
- [ ] File `.env` sudah dikonfigurasi

---

> **Selanjutnya:** Lanjut ke [02-database-models.md](./02-database-models.md)
