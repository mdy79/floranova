from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from floranova.database import get_db
from floranova.models.inventory import FlowerFreshnessBatch, FreshnessStatus
from floranova.models.user import User
from floranova.schemas.inventory import (
    BatchCreate,
    BatchUpdate,
    BatchOut,
    InventorySummaryOut,
)
from floranova.core.security import require_staff

router = APIRouter(prefix="/inventory", tags=["Perishable Inventory"])


@router.get("/batches", response_model=List[BatchOut])
async def list_batches(
    status_filter: Optional[FreshnessStatus] = None,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(FlowerFreshnessBatch)
    if status_filter:
        stmt = stmt.where(FlowerFreshnessBatch.status == status_filter)
    stmt = stmt.order_by(FlowerFreshnessBatch.received_date.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/batches", response_model=BatchOut, status_code=status.HTTP_201_CREATED)
async def create_batch(
    payload: BatchCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    # Check duplicate batch code
    stmt = select(FlowerFreshnessBatch).where(FlowerFreshnessBatch.batch_code == payload.batch_code)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"شناسه بچ '{payload.batch_code}' قبلاً ثبت شده است",
        )

    batch = FlowerFreshnessBatch(
        batch_code=payload.batch_code,
        flower_species=payload.flower_species,
        stems_received=payload.stems_received,
        stems_remaining=payload.stems_remaining,
        unit_cost_toman=payload.unit_cost_toman,
        max_freshness_days=payload.max_freshness_days,
        status=FreshnessStatus.FRESH,
        notes=payload.notes,
    )
    db.add(batch)
    await db.commit()
    await db.refresh(batch)
    return batch


@router.patch("/batches/{batch_id}", response_model=BatchOut)
async def update_batch(
    batch_id: int,
    payload: BatchUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(FlowerFreshnessBatch).where(FlowerFreshnessBatch.id == batch_id)
    result = await db.execute(stmt)
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="بچ گل مورد نظر یافت نشد",
        )

    if payload.stems_remaining is not None:
        batch.stems_remaining = payload.stems_remaining
    if payload.status is not None:
        batch.status = payload.status
    if payload.notes is not None:
        batch.notes = payload.notes

    await db.commit()
    await db.refresh(batch)
    return batch


@router.get("/summary", response_model=InventorySummaryOut)
async def get_inventory_summary(
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(FlowerFreshnessBatch)
    result = await db.execute(stmt)
    batches = result.scalars().all()

    fresh_stems = sum(b.stems_remaining for b in batches if b.status == FreshnessStatus.FRESH)
    rotating_stems = sum(b.stems_remaining for b in batches if b.status == FreshnessStatus.NEEDS_ROTATION)
    wasted_stems = sum(b.stems_received - b.stems_remaining for b in batches if b.status == FreshnessStatus.EXPIRED_WASTED)
    active_batches = len([b for b in batches if b.stems_remaining > 0])

    total_active_stems = fresh_stems + rotating_stems
    spoilage_risk = (
        round((rotating_stems / total_active_stems) * 100, 1)
        if total_active_stems > 0
        else 0.0
    )

    return InventorySummaryOut(
        total_stems_fresh=fresh_stems,
        total_stems_rotating=rotating_stems,
        total_stems_wasted=wasted_stems,
        active_batches_count=active_batches,
        spoilage_risk_percentage=spoilage_risk,
    )
