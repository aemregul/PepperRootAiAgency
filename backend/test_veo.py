"""Veo 3.1 Fast test — tam sonuç dosyaya yazılır."""
import sys, time, traceback
sys.path.insert(0, '.')

OUT = "/tmp/veo_test_result.txt"

def log(msg):
    with open(OUT, "a") as f:
        f.write(msg + "\n")
    print(msg, flush=True)

# Clear
with open(OUT, "w") as f:
    f.write("")

try:
    from app.core.config import settings
    from google import genai
    from google.genai import types
    
    log(f"API_KEY: {settings.GEMINI_API_KEY[:10]}...")
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    config = types.GenerateVideosConfig(
        aspect_ratio='16:9',
        person_generation='allow_all',
        number_of_videos=1,
    )

    log("Creating Veo operation...")
    op = client.models.generate_videos(
        model='veo-3.1-fast-generate-preview',
        prompt='A calm sunset over the ocean',
        config=config,
    )
    log(f"OP name={op.name}")
    log(f"OP done={op.done}")
    
    log("Polling...")
    for i in range(12):
        time.sleep(10)
        try:
            op = client.operations.get(op)
            log(f"Poll #{i+1}: done={op.done}")
            if op.done:
                if op.error:
                    log(f"ERROR: {op.error}")
                else:
                    result = op.result
                    if result and result.generated_videos:
                        v = result.generated_videos[0]
                        log(f"SUCCESS! URI={v.video.uri}")
                    else:
                        log(f"No videos: {result}")
                break
        except Exception as e:
            log(f"POLL_ERR: {type(e).__name__}: {e}")
            log(traceback.format_exc())
            break
    else:
        log("TIMEOUT 2min")

except Exception as e:
    log(f"FATAL: {type(e).__name__}: {e}")
    log(traceback.format_exc())
