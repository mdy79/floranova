from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from floranova.database import get_db
from floranova.models.user import User, UserRole
from floranova.schemas.user import UserRegister, UserLogin, UserOut, TokenResponse
from floranova.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    require_authenticated_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check existing email
    stmt = select(User).where(User.email == payload.email)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این آدرس ایمیل قبلاً در سیستم ثبت شده است",
        )

    # Check existing phone if provided
    if payload.phone_number:
        stmt_phone = select(User).where(User.phone_number == payload.phone_number)
        existing_phone = (await db.execute(stmt_phone)).scalar_one_or_none()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این شماره همراه قبلاً در سیستم ثبت شده است",
            )

    user = User(
        email=payload.email,
        phone_number=payload.phone_number,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا کلمه عبور وارد شده نادرست است",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما غیرفعال شده است",
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(require_authenticated_user)):
    return current_user
