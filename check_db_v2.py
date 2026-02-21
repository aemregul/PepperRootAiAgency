
import asyncio
import uuid
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.models import GeneratedAsset, Message

async def check_assets():
    async with async_session_maker() as db:
        # Son 10 asset'i kontrol et
        result = await db.execute(
            select(GeneratedAsset).order_by(GeneratedAsset.created_at.desc()).limit(10)
        )
        assets = result.scalars().all()
        print("--- RECENT ASSETS ---")
        for a in assets:
            print(f"ID: {a.id}, Type: {a.asset_type}, Model: {a.model_name}, Created: {a.created_at}")
            print(f"  URL: {a.url}")
            print(f"  Prompt: {a.prompt}")
            print("-" * 20)

        # Son 10 mesajı kontrol et (özellikle metadata)
        result = await db.execute(
            select(Message).order_by(Message.created_at.desc()).limit(10)
        )
        messages = result.scalars().all()
        print("\n--- RECENT MESSAGES ---")
        for m in messages:
            print(f"ID: {m.id}, Role: {m.role}, Created: {m.created_at}")
            print(f"  Content: {m.content[:200]}...")
            print(f"  Metadata: {m.metadata_}")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(check_assets())
