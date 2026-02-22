import asyncio
from sqlalchemy import select, desc
from app.core.database import async_session_maker
from app.models.models import MediaAsset

async def main():
    async with async_session_maker() as session:
        result = await session.execute(
            select(MediaAsset).where(MediaAsset.asset_type == "video").order_by(desc(MediaAsset.created_at)).limit(3)
        )
        assets = result.scalars().all()
        for a in assets:
            print(f"[{a.created_at}] URL: {a.url} | Model: {a.model_name}")

if __name__ == "__main__":
    asyncio.run(main())
