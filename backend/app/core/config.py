"""Central application settings, loaded from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    app_name: str = "ITNEXT Global Careers API"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://itnext:itnext@db:5432/itnext"

    # --- Auth / JWT ---
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000"]

    # --- External services ---
    gemini_api_key: str = ""
    azure_storage_connection_string: str = ""
    azure_blob_container: str = "cvs"

    # Base URL the browser can reach this API on — used to build the local-disk
    # CV upload URL when neither Backblaze B2 nor Azure Blob is configured (see
    # modules/cv/service.py).
    api_public_url: str = "http://localhost:8000"
    # Where CVs land on disk in that fallback path. Relative paths resolve
    # against the container's working directory (/code), which is bind-mounted
    # to ./backend on the host, so uploads survive container restarts.
    cv_storage_dir: str = "data/cvs"

    # --- Backblaze B2 (S3-compatible CV storage) ---
    # Blank = CVs fall back to local disk (cv_storage_dir above). All four
    # must be set for B2 to activate — see modules/cv/service.py. Private
    # buckets on B2 don't require a card on file (unlike Cloudflare R2).
    b2_endpoint: str = ""  # e.g. https://s3.us-west-004.backblazeb2.com
    b2_region: str = ""  # e.g. us-west-004 (the part after "s3." in the endpoint)
    b2_key_id: str = ""
    b2_application_key: str = ""
    b2_bucket_name: str = "cvs"

    # --- Payments (PayHere) ---
    payhere_merchant_id: str = ""
    payhere_merchant_secret: str = ""
    payhere_sandbox: bool = True

    # --- Google sign-in ---
    # OAuth 2.0 Web Client ID from Google Cloud Console. Blank = the Google
    # button simply doesn't render (see /auth/config) — no other code path
    # depends on it, same boots-with-zero-credentials pattern as Azure/PayHere.
    google_client_id: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
