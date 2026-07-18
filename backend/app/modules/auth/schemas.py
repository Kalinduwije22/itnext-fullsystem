import re

from pydantic import BaseModel, EmailStr, Field, field_validator

PHONE_PATTERN = r"^\+[1-9]\d{6,14}$"  # E.164: leading + and country code


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8)
    phone: str = Field(pattern=PHONE_PATTERN)

    @field_validator("full_name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return stripped

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("Password must contain at least one letter and one number")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_admin: bool = False
    phone: str | None = None

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GoogleLoginIn(BaseModel):
    credential: str


class AuthConfigOut(BaseModel):
    google_client_id: str
