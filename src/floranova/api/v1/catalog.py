from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from floranova.database import get_db
from floranova.models.product import Category, Product, AddonItem, ArrangementType
from floranova.schemas.product import (
    CategoryOut,
    ProductListItemOut,
    ProductDetailOut,
    AddonOut,
)

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    stmt = select(Category).where(Category.is_active == True).order_by(Category.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/products", response_model=List[ProductListItemOut])
async def list_products(
    category_slug: Optional[str] = None,
    arrangement_type: Optional[ArrangementType] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Product).where(Product.is_available == True)

    if category_slug:
        stmt = stmt.join(Product.category).where(Category.slug == category_slug)

    if arrangement_type:
        stmt = stmt.where(Product.arrangement_type == arrangement_type)

    if is_featured is not None:
        stmt = stmt.where(Product.is_featured == is_featured)

    if search:
        search_term = f"%{search.strip()}%"
        stmt = stmt.where(
            (Product.title_fa.ilike(search_term))
            | (Product.title_en.ilike(search_term))
            | (Product.description_fa.ilike(search_term))
        )

    stmt = stmt.order_by(Product.is_featured.desc(), Product.id.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/products/{slug}", response_model=ProductDetailOut)
async def get_product_detail(slug: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.slug == slug, Product.is_available == True)
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول مورد نظر یافت نشد",
        )
    return product


@router.get("/addons", response_model=List[AddonOut])
async def list_addons(db: AsyncSession = Depends(get_db)):
    stmt = select(AddonItem).where(AddonItem.is_active == True).order_by(AddonItem.id)
    result = await db.execute(stmt)
    return result.scalars().all()
