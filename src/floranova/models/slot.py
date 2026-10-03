from sqlalchemy import String, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from floranova.database import Base


class DeliverySlot(Base):
    __tablename__ = "delivery_slots"
    __table_args__ = (
        UniqueConstraint("date_jalali", "time_window", name="uq_slot_date_window"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_jalali: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    time_window: Mapped[str] = mapped_column(String(32), nullable=False)
    label_fa: Mapped[str] = mapped_column(String(64), nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    reserved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    @property
    def is_available(self) -> bool:
        return self.is_active and (self.reserved_count < self.max_capacity)

    @property
    def remaining_capacity(self) -> int:
        return max(0, self.max_capacity - self.reserved_count)
