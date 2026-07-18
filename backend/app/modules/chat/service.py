"""AI career assistant backed by the Gemini API.

This replaces real-time human chat: the user 'chats', the model answers
(CV feedback, career Q&A, package guidance). No WebSocket / Redis needed.
History is persisted so each request has context.
"""
from google import genai
from google.genai import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.chat.models import ChatMessage

SYSTEM_PROMPT = (
    "You are the ITNEXT Global Careers assistant. Help Sri Lankan professionals "
    "with CV feedback, interview prep, and guidance on international career moves. "
    "Be concise, practical, and encouraging."
)


async def _history(db: AsyncSession, user_id: str) -> list[dict]:
    rows = await db.scalars(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at)
    )
    # Gemini uses "model" rather than "assistant" for the reply role.
    return [
        {"role": "model" if r.role == "assistant" else "user", "parts": [{"text": r.content}]}
        for r in rows
    ]


async def send(db: AsyncSession, user_id: str, message: str) -> str:
    history = await _history(db, user_id)
    history.append({"role": "user", "parts": [{"text": message}]})

    reply = "(assistant stub — set GEMINI_API_KEY to enable live replies)"
    if settings.gemini_api_key:
        client = genai.Client(api_key=settings.gemini_api_key)
        resp = await client.aio.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=history,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        reply = resp.text

    db.add(ChatMessage(user_id=user_id, role="user", content=message))
    db.add(ChatMessage(user_id=user_id, role="assistant", content=reply))
    await db.flush()
    return reply
