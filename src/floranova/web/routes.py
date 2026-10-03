from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from floranova.database import get_db
from floranova.models.product import Category, Product, AddonItem
from floranova.models.order import Order
from floranova.core.dates import get_available_delivery_dates, format_jalali_friendly, get_today_jalali
from floranova.config import settings

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Register template filters
templates.env.filters["format_toman"] = lambda val: f"{val:,.0f} {settings.CURRENCY_NAME}" if val is not None else "-"
templates.env.filters["jalali_friendly"] = format_jalali_friendly

web_router = APIRouter(include_in_schema=False)


@web_router.get("/", response_class=HTMLResponse)
async def storefront_page(request: Request, db: AsyncSession = Depends(get_db)):
    categories_res = await db.execute(select(Category).where(Category.is_active == True))
    categories = categories_res.scalars().all()

    products_res = await db.execute(
        select(Product).options(selectinload(Product.category)).where(Product.is_available == True)
    )
    products = products_res.scalars().all()

    addons_res = await db.execute(select(AddonItem).where(AddonItem.is_active == True))
    addons = addons_res.scalars().all()

    delivery_dates = get_available_delivery_dates(days_ahead=7)

    return templates.TemplateResponse(
        request=request,
        name="storefront.html",
        context={
            "categories": categories,
            "products": products,
            "addons": addons,
            "delivery_dates": delivery_dates,
            "settings": settings,
        },
    )


@web_router.get("/track/{tracking_code}", response_class=HTMLResponse)
async def tracking_page(tracking_code: str, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.addons))
        .where(Order.tracking_code == tracking_code.strip().upper())
    )
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    if not order:
        return templates.TemplateResponse(
            request=request,
            name="order_track.html",
            context={"order": None, "tracking_code": tracking_code, "settings": settings},
            status_code=404,
        )

    return templates.TemplateResponse(
        request=request,
        name="order_track.html",
        context={"order": order, "tracking_code": tracking_code, "settings": settings},
    )


@web_router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request, db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "settings": settings,
            "today_jalali": get_today_jalali(),
        },
    )
