"""Grant admin access to an existing user.

Deliberately NOT reachable over HTTP — the account must already exist
(register normally first), and this must be run by whoever has shell/DB
access to the server, e.g. `make promote-admin EMAIL=you@example.com`.
That keeps admin promotion off the public attack surface entirely: no
endpoint, form, or email-based auto-promotion that a stranger who learns
or guesses the admin's email could exploit by registering first.
"""
import asyncio
import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.modules.auth.models import User


async def main(email: str) -> None:
    async with SessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == email))
        if not user:
            print(f"No user with email {email!r} — register the account first.")
            raise SystemExit(1)
        if user.is_admin:
            print(f"{email} is already an admin.")
            return
        user.is_admin = True
        await db.commit()
    print(f"{email} is now an admin.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m app.promote_admin <email>")
        raise SystemExit(1)
    asyncio.run(main(sys.argv[1]))
