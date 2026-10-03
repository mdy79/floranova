import enum
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, Boolean, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from floranova.database import Base


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"        # در انتظار پرداخت
    CONFIRMED = "CONFIRMED"                    # تایید شده و ارجاع به کارگاه
    ARRANGING = "ARRANGING"                    # در حال دیزاین توسط کارشناس گلآرایی
    QUALITY_APPROVED = "QUALITY_APPROVED"      # کنترل کیفی و تایید تصویر ژورنالی
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"      # تحویل به پیک اختصاصی فلورانوا
    DELIVERED = "DELIVERED"                    # تحویل موفق به گیرنده
    CANCELLED = "CANCELLED"                    # لغو شده


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tracking_code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.CONFIRMED, nullable=False, index=True
    )
    
    # Customer reference (nullable for guest checkout)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    
    # Buyer Contact Details
    buyer_name: Mapped[str] = mapped_column(String(128), nullable=False)
    buyer_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    buyer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Recipient Details (Logistics)
    recipient_name: Mapped[str] = mapped_column(String(128), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    recipient_address: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_city: Mapped[str] = mapped_column(String(64), default="تهران", nullable=False)
    district_zone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Floristry Gifting & Surprise Options
    is_surprise: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    greeting_card_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    greeting_card_sender: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    ribbon_text: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # Scheduled Delivery Slot
    delivery_date_jalali: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    delivery_time_window: Mapped[str] = mapped_column(String(64), nullable=False)
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pricing Breakdown (Toman)
    items_total: Mapped[int] = mapped_column(Integer, nullable=False)
    addons_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delivery_fee: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    discount_amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    final_total: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Florist Quality Inspection & Live Timeline
    arrangement_photo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status_history: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    customer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    addons = relationship("OrderAddon", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_title: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class OrderAddon(Base):
    __tablename__ = "order_addons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    addon_id: Mapped[int] = mapped_column(ForeignKey("addon_items.id"), nullable=False)
    addon_title: Mapped[str] = mapped_column(String(128), nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False)

    order = relationship("Order", back_populates="addons")
    addon = relationship("AddonItem")
