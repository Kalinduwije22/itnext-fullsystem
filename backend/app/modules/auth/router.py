from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth import service
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    AuthConfigOut,
    GoogleLoginIn,
    TokenOut,
    UserCreate,
    UserLogin,
    UserOut,
)
from app.shared.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/config", response_model=AuthConfigOut)
async def auth_config():
    return AuthConfigOut(google_client_id=settings.google_client_id)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await service.register(db, data)


@router.post("/login", response_model=TokenOut)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    token = await service.authenticate(db, data)
    return TokenOut(access_token=token)


@router.post("/google", response_model=TokenOut)
async def google_login(data: GoogleLoginIn, db: AsyncSession = Depends(get_db)):
    token = await service.google_login(db, data.credential)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user
