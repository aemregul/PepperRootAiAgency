import asyncio
import sys
from app.core.database import async_session_maker
from app.models.models import Message
from sqlalchemy import select

async def main():
    async with async_session_maker() as db:
        result = await db.execute(select(Message).where(Message.content.like('%⚠️ Beklenmeyen Sistem Hatası%')).order_by(Message.created_at.desc()).limit(1))
        msg = result.scalar_one_or_none()
        if msg:
            print(f"FOUND ERROR: {msg.content}")
        else:
            print("No error message found in DB.")

if __name__ == "__main__":
    asyncio.run(main())
