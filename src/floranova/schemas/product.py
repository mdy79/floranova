from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from floranova.models.product import ArrangementType, AddonType


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name_fa: str
    name_en: str
    description: Optional[str]
    is_active: bool


class AddonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title_fa: str
    addon_type: AddonType
    price: int
    image_url: str
    is_active: bool


class ProductListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title_fa: str
    title_en: str
    price: int
    discount_price: Optional[int]
    arrangement_type: ArrangementType
    primary_image: str
    flower_types: List[str]
    stem_count: int
    vase_included: bool
    is_featured: bool
    is_available: bool


class ProductDetailOut(ProductListItemOut):
    model_config = ConfigDict(from_attributes=True)

    description_fa: str
    estimated_prep_time_minutes: int
    gallery_images: List[str]
    category: CategoryOut


class ProductCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=128)
    title_fa: str = Field(..., min_length=2, max_length=255)
    title_en: str = Field(..., min_length=2, max_length=255)
    description_fa: str
    price: int = Field(..., gt=0)
    discount_price: Optional[int] = None
    category_id: int
    arrangement_type: ArrangementType = ArrangementType.BOUQUET
    flower_types: List[str] = Field(default_factory=list)
    stem_count: int = Field(12, ge=1)
    vase_included: bool = False
    estimated_prep_time_minutes: int = Field(45, ge=10)
    primary_image: str
    gallery_images: List[str] = Field(default_factory=list)
    is_featured: bool = False
    is_available: bool = True
