"""Seed the four packages with the recommended LKR pricing."""
import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.modules.packages.models import Package

PACKAGES = [
    ("starter", "Starter", 29900, "Career assessment, CV review, LinkedIn review, job search guide."),
    ("professional", "Professional", 89900, "Everything in Starter + interview coaching, 20 applications, cover letters."),
    ("premium", "Premium", 169900, "Everything in Professional + unlimited applications, priority support, employer introductions."),
    ("vip", "VIP", 349900, "End-to-end service: dedicated advisor, weekly meetings, relocation support, salary negotiation."),
]


async def main():
    async with SessionLocal() as db:
        for slug, name, price, desc in PACKAGES:
            exists = await db.scalar(select(Package).where(Package.slug == slug))
            if not exists:
                db.add(Package(slug=slug, name=name, price_lkr=price, description=desc))
        await db.commit()
    print("Seeded packages.")


if __name__ == "__main__":
    asyncio.run(main())
