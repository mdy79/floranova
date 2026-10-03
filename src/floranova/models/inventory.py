import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column
from floranova.database import Base


class FreshnessStatus(str, enum.Enum):
    FRESH = "FRESH"                       # شاداب و درجه یک
    NEEDS_ROTATION = "NEEDS_ROTATION"     # نزدیک به افت کیفیت (پیشنهاد فروش ویژه)
    EXPIRED_WASTED = "EXPIRED_WASTED"     # پلاسیده / ثبت در ضایعات


class FlowerFreshnessBatch(Base):
    __tablename__ = "flower_batches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    flower_species: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    stems_received: Mapped[int] = mapped_column(Integer, nullable=False)
    stems_remaining: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost_toman: Mapped[int] = mapped_column(Integer, nullable=False)
    
    received_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    max_freshness_days: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    status: Mapped[FreshnessStatus] = mapped_column(
        Enum(FreshnessStatus), default=FreshnessStatus.FRESH, nullable=False, index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
