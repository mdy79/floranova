from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from floranova.config import settings
from floranova.database import get_db
from floranova.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        return None
    return user


async def require_authenticated_user(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="احراز هویت الزامی است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def require_admin(
    current_user: User = Depends(require_authenticated_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی مجاز نمیباشد (سطح مدیر مورد نیاز است)",
        )
    return current_user


async def require_staff(
    current_user: User = Depends(require_authenticated_user),
) -> User:
    if current_user.role not in (UserRole.ADMIN, UserRole.FLORIST):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی مجاز نمیباشد (پرسنل کارگاه و دیزاین)",
        )
    return current_user
