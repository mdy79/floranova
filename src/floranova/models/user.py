import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from floranova.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    FLORIST = "FLORIST"
    CUSTOMER = "CUSTOMER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.CUSTOMER, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
