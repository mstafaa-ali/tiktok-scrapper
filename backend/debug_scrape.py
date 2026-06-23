"""Debug script: test scraper dengan fix timeout + retry."""
import asyncio
import sys
import traceback

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_scrape():
    from TikTokApi import TikTokApi

    video_url = "https://www.tiktok.com/@pandawaragroup/video/7547692677559487749"

    print(f"[1] Memulai scraping: {video_url}")
    print(f"    - timeout: 60000ms")
    print(f"    - suppress: image, media, font, stylesheet")
    print(f"    - sleep_after: 5s")
    print()

    try:
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=None,
                num_sessions=1,
                sleep_after=5,
                headless=False,
                timeout=60000,
                suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            )
            print("[2] Session created successfully")

            video_id = "7547692677559487749"
            video = api.video(id=video_id, url=video_url)
            print(f"[3] Video object created")

            comments = []
            async for comment in video.comments(count=10):
                comments.append({
                    "id": comment.id,
                    "text": comment.text,
                })
                print(f"    Comment #{len(comments)}: {comment.text[:80] if comment.text else '(empty)'}...")

            print(f"\n[SUCCESS] Total komentar: {len(comments)}")

    except Exception as e:
        print(f"\n[FAILED] {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scrape())
