import asyncio
import asyncpg

async def create_db():
    try:
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5432/postgres')
        try:
            await conn.execute('CREATE DATABASE tiktok_scraper_test')
            print("Database created successfully")
        except asyncpg.exceptions.DuplicateDatabaseError:
            print("Database already exists")
        await conn.close()
    except Exception as e:
        print(f"Failed to create db: {e}")

asyncio.run(create_db())
