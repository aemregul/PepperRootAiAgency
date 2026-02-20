import asyncio
import os
from app.services.gemini_image_service import gemini_image_service

async def run():
    # Sample image URL from what might have been used
    url = "https://v3.fal.media/files/lion/WjJcM2lY6ZlqC0xQnZQz7.png" 
    
    # Simulate the orchestrator prompt enrichment
    prompt = "Create a catalog advertisement image, background should fit the brand. 8k resolution, cinematic lighting, photorealistic."
    
    res = await gemini_image_service.generate_with_reference(
        prompt=prompt,
        reference_image_url=url,
        aspect_ratio="16:9"
    )
    print("RESULT:", res)

if __name__ == "__main__":
    asyncio.run(run())
