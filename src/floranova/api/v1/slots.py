from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from floranova.database import get_db
from floranova.models.slot import DeliverySlot
from floranova.config import settings
from floranova.core.dates import get_available_delivery_dates

router = APIRouter(prefix="/slots", tags=["Delivery Slots"])

DEFAULT_TIME_WINDOWS = [
    {"time_window": "09:00-13:00", "label_fa": "بازه صبح (۰۹:۰۰ الی ۱۳:۰۰)"},
    {"time_window": "13:00-17:00", "label_fa": "بازه عصر (۱۳:۰۰ الی ۱۷:۰۰)"},
    {"time_window": "17:00-21:00", "label_fa": "بازه شب (۱۷:۰۰ الی ۲۱:۰۰)"},
]


@router.get("/dates")
async def list_available_dates():
    return get_available_delivery_dates(days_ahead=7)


@router.get("/windows")
async def get_windows_for_date(
    date_jalali: str = Query(..., pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"),
    db: AsyncSession = Depends(get_db),
):
    # Query existing slots for this date
    stmt = select(DeliverySlot).where(DeliverySlot.date_jalali == date_jalali)
    result = await db.execute(stmt)
    slots = {s.time_window: s for s in result.scalars().all()}

    # Auto-initialize default slots for this date if missing
    created_any = False
    for item in DEFAULT_TIME_WINDOWS:
        w = item["time_window"]
        if w not in slots:
            new_slot = DeliverySlot(
                date_jalali=date_jalali,
                time_window=w,
                label_fa=item["label_fa"],
                max_capacity=settings.MAX_SLOT_CAPACITY,
                reserved_count=0,
                is_active=True,
            )
            db.add(new_slot)
            slots[w] = new_slot
            created_any = True

    if created_any:
        await db.commit()

    output = []
    for item in DEFAULT_TIME_WINDOWS:
        w = item["time_window"]
        slot_obj = slots[w]
        output.append({
            "id": slot_obj.id,
            "date_jalali": slot_obj.date_jalali,
            "time_window": slot_obj.time_window,
            "label_fa": slot_obj.label_fa,
            "max_capacity": slot_obj.max_capacity,
            "reserved_count": slot_obj.reserved_count,
            "remaining_capacity": slot_obj.remaining_capacity,
            "is_available": slot_obj.is_available,
        })

    return output
