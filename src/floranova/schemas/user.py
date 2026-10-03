from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from floranova.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=128)
    password: str = Field(..., min_length=6)
    phone_number: Optional[str] = Field(None, pattern=r"^09[0-9]{9}$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    phone_number: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
