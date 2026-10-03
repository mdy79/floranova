from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from floranova.database import get_db
from floranova.models.order import Order, OrderStatus
from floranova.models.inventory import FlowerFreshnessBatch, FreshnessStatus
from floranova.models.user import User
from floranova.schemas.order import AdminStatsOut
from floranova.core.security import require_staff
from floranova.core.dates import get_today_jalali

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get("/stats", response_model=AdminStatsOut)
async def get_dashboard_stats(
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    today_j = get_today_jalali()

    # Revenue from non-cancelled orders
    rev_stmt = select(func.coalesce(func.sum(Order.final_total), 0)).where(
        Order.status != OrderStatus.CANCELLED
    )
    rev_res = await db.execute(rev_stmt)
    total_revenue = rev_res.scalar_one()

    # Today's orders count
    today_stmt = select(func.count(Order.id)).where(
        Order.delivery_date_jalali == today_j,
        Order.status != OrderStatus.CANCELLED,
    )
    today_orders = (await db.execute(today_stmt)).scalar_one()

    # Status counts
    arranging_stmt = select(func.count(Order.id)).where(Order.status == OrderStatus.ARRANGING)
    active_arranging = (await db.execute(arranging_stmt)).scalar_one()

    out_delivery_stmt = select(func.count(Order.id)).where(Order.status == OrderStatus.OUT_FOR_DELIVERY)
    out_for_delivery = (await db.execute(out_delivery_stmt)).scalar_one()

    delivered_stmt = select(func.count(Order.id)).where(Order.status == OrderStatus.DELIVERED)
    delivered = (await db.execute(delivered_stmt)).scalar_one()

    pending_stmt = select(func.count(Order.id)).where(
        Order.status.in_([OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED])
    )
    pending = (await db.execute(pending_stmt)).scalar_one()

    # Inventory metrics
    batch_stmt = select(FlowerFreshnessBatch)
    batches = (await db.execute(batch_stmt)).scalars().all()

    fresh_stems = sum(b.stems_remaining for b in batches if b.status == FreshnessStatus.FRESH)
    rotating_stems = sum(b.stems_remaining for b in batches if b.status == FreshnessStatus.NEEDS_ROTATION)
    total_active = fresh_stems + rotating_stems
    spoilage_risk = (
        round((rotating_stems / total_active) * 100, 1)
        if total_active > 0
        else 0.0
    )

    return AdminStatsOut(
        total_revenue_toman=int(total_revenue),
        today_orders_count=today_orders,
        active_arranging_count=active_arranging,
        out_for_delivery_count=out_for_delivery,
        delivered_count=delivered,
        pending_count=pending,
        active_fresh_stems=fresh_stems,
        spoilage_risk_percent=spoilage_risk,
    )
