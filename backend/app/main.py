"""Application entrypoint — a modular monolith.

Each module under app/modules owns its models, schemas, service, and router.
Modules talk to each other only through their service layer, so any one of
them (e.g. cv or chat) can be extracted into its own service later without
rewiring the rest.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Import models so Alembic's autogenerate sees them via Base.metadata.
from app.modules.admin.router import router as admin_router  # no models of its own
from app.modules.assessment import models as _assessment  # noqa: F401
from app.modules.assessment.router import router as assessment_router
from app.modules.auth import models as _auth  # noqa: F401
from app.modules.auth.router import router as auth_router
from app.modules.chat import models as _chat  # noqa: F401
from app.modules.chat.router import router as chat_router
from app.modules.cv import models as _cv  # noqa: F401
from app.modules.cv.router import router as cv_router
from app.modules.packages import models as _packages  # noqa: F401
from app.modules.packages.router import router as packages_router
from app.modules.payments import models as _payments  # noqa: F401
from app.modules.payments.router import router as payments_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "environment": settings.environment}


for r in (
    auth_router,
    packages_router,
    cv_router,
    assessment_router,
    chat_router,
    payments_router,
    admin_router,
):
    app.include_router(r, prefix=settings.api_prefix)
