from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.chat import service
from app.modules.chat.schemas import ChatIn, ChatOut
from app.shared.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatOut)
async def chat(
    data: ChatIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    reply = await service.send(db, user.id, data.message)
    return ChatOut(reply=reply)
