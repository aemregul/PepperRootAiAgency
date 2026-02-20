import asyncio
import uuid
from app.services.agent.orchestrator import AgentOrchestrator
from app.api.routes.chat import chat
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker

async def run_test():
    agent = AgentOrchestrator()
    session_id = uuid.uuid4()
    
    # Simulate DB session
    class DummyDB:
        pass
    db = DummyDB()
    
    # 1. Provide two images from "history"
    last_reference_urls = [
        "https://v3b.fal.media/files/b/0a8f4698/xxx1.jpg",
        "https://v3b.fal.media/files/b/0a8f4698/xxx2.jpg"
    ]
    
    # 2. Call process_message
    try:
        res = await agent.process_message(
            user_message="ikinci karakter görselde yok onu eklemen lazım",
            session_id=session_id,
            db=db,
            conversation_history=[
                {"role": "user", "content": "nike katalog reklam çekimi..."}
            ],
            reference_image=None,
            reference_images=None,
            last_reference_urls=last_reference_urls
        )
        print("Agent Response Keys:", res.keys())
        print("Current Uploaded URLs:", agent._current_uploaded_urls)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
