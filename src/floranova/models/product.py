import enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from floranova.database import Base


class ArrangementType(str, enum.Enum):
    BOUQUET = "BOUQUET"        # دسته گل
    BOX = "BOX"                # باکس گل
    BASKET = "BASKET"          # سبد گل
    VASE = "VASE"              # گلدان چیدمان
    STAND = "STAND"            # تاج و استند تشریفاتی


class AddonType(str, enum.Enum):
    GREETING_CARD = "GREETING_CARD"  # کارت پستال نفیس
    CHOCOLATE = "CHOCOLATE"          # شکلات دستساز
    BALLOON = "BALLOON"              # بادکنک هلیومی
    VASE = "VASE"                    # گلدان شیشهای/سرامیکی
    TOPPER = "TOPPER"                # تاپر چوبی و تزیینی


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name_fa: Mapped[str] = mapped_column(String(128), nullable=False)
    name_en: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    title_fa: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_fa: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # Toman
    discount_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)
    arrangement_type: Mapped[ArrangementType] = mapped_column(
        Enum(ArrangementType), default=ArrangementType.BOUQUET, nullable=False, index=True
    )
    
    flower_types: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    stem_count: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    vase_included: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_prep_time_minutes: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    
    primary_image: Mapped[str] = mapped_column(String(512), nullable=False)
    gallery_images: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class AddonItem(Base):
    __tablename__ = "addon_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title_fa: Mapped[str] = mapped_column(String(128), nullable=False)
    addon_type: Mapped[AddonType] = mapped_column(Enum(AddonType), nullable=False, index=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # Toman
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
