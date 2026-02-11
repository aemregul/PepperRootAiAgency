import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.services.plugins.fal_plugin_v2 import FalPluginV2

async def debug_video_edit():
    print("🚀 Debugging Video Edit Flow...")
    
    # Check Keys
    print(f"🔑 FAL_KEY: {'Expected' if settings.FAL_KEY else 'MISSING'}")
    print(f"🔑 OPENAI_API_KEY: {'Expected' if settings.OPENAI_API_KEY else 'MISSING'}")
    
    plugin = FalPluginV2()
    
    # Test Case: Remove cat from video (Simulated)
    # Using a dummy video URL that looks valid
    test_video_url = "https://storage.googleapis.com/falserverless/gallery/kling-sample.mp4"
    test_prompt = "videodaki kediyi sil"
    
    print(f"\n🎬 Testing _edit_video with prompt: '{test_prompt}'")
    print(f"   Video URL: {test_video_url}")
    
    try:
        result = await plugin._edit_video({
            "video_url": test_video_url,
            "prompt": test_prompt,
            "image_url": None # Force extraction logic
        })
        
        print("\n✅ RESULT:")
        print(result)
        
    except Exception as e:
        print("\n❌ CRITICAL EXCEPTION:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_video_edit())
