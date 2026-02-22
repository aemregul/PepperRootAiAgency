#!/bin/bash
tail -n 100 ~/.gemini/antigravity/brain/bc9a4664-ea82-43fd-9355-b1654dc80f8b/.system_generated/logs/backend.log 2>/dev/null || true
tail -n 100 /tmp/uvicorn.log 2>/dev/null || true
