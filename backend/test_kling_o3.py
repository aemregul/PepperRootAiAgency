import asyncio
import fal_client
import sys

async def main():
    url = "https://v3b.fal.media/files/b/0a8f6903/8-haaHFhDvOlYmdIuKwv4_tmp5xbsc7uy.jpg"
    ep = "fal-ai/kling-video/o3/standard/image-to-video"
    print(f"Testing {ep}...")
    try:
        res = await fal_client.submit_async(
            ep,
            arguments={"image_url": url, "prompt": "Test video"}
        )
        print(f"✅ Success SUBMIT: {res}")
        status = await fal_client.status_async("fal-ai/kling-video/o3/standard/image-to-video", res.request_id, with_logs=True)
        print(f"STATUS IS: {status}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
