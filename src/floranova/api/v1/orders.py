import random
import string
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from floranova.database import get_db
from floranova.config import settings
from floranova.models.order import Order, OrderItem, OrderAddon, OrderStatus
from floranova.models.product import Product, AddonItem
from floranova.models.slot import DeliverySlot
from floranova.models.user import User
from floranova.schemas.order import (
    CheckoutRequest,
    OrderDetailOut,
    OrderListItemOut,
    OrderStatusTransitionRequest,
    PublicOrderTrackOut,
)
from floranova.core.security import (
    get_current_user,
    require_authenticated_user,
    require_staff,
)
from floranova.core.state_machine import (
    apply_order_transition,
    STATUS_TITLES_FA,
    InvalidStateTransitionError,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_tracking_code() -> str:
    nums = "".join(random.choices(string.digits, k=6))
    return f"FN-{nums}"


def mask_name(name: str) -> str:
    parts = name.split()
    masked_parts = []
    for p in parts:
        if len(p) <= 2:
            masked_parts.append(p[0] + "*")
        else:
            masked_parts.append(p[0] + "*" * (len(p) - 2) + p[-1])
    return " ".join(masked_parts)


@router.post("/checkout", response_model=OrderDetailOut, status_code=status.HTTP_201_CREATED)
async def create_checkout_order(
    payload: CheckoutRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Validate & Lock Delivery Slot
    slot_stmt = select(DeliverySlot).where(
        DeliverySlot.date_jalali == payload.delivery_date_jalali,
        DeliverySlot.time_window == payload.delivery_time_window,
    )
    slot_res = await db.execute(slot_stmt)
    slot = slot_res.scalar_one_or_none()

    if not slot:
        # Create slot automatically if not present
        slot = DeliverySlot(
            date_jalali=payload.delivery_date_jalali,
            time_window=payload.delivery_time_window,
            label_fa=f"بازه {payload.delivery_time_window}",
            max_capacity=settings.MAX_SLOT_CAPACITY,
            reserved_count=0,
            is_active=True,
        )
        db.add(slot)
        await db.flush()

    if not slot.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ظرفیت کارگاه گلآرایی برای این بازه زمانی تکمیل شده است. لطفاً بازه یا روز دیگری را انتخاب کنید.",
        )

    # Increment slot reservation
    slot.reserved_count += 1

    # 2. Fetch and Validate Products
    product_ids = [item.product_id for item in payload.items]
    prod_stmt = select(Product).where(Product.id.in_(product_ids), Product.is_available == True)
    prod_res = await db.execute(prod_stmt)
    products_by_id = {p.id: p for p in prod_res.scalars().all()}

    if len(products_by_id) != len(set(product_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="برخی از محصولات انتخابی نامعتبر یا ناموجود هستند",
        )

    items_total = 0
    order_items_to_create = []
    for item in payload.items:
        prod = products_by_id[item.product_id]
        unit_price = prod.discount_price if prod.discount_price else prod.price
        subtotal = unit_price * item.quantity
        items_total += subtotal
        order_items_to_create.append(
            OrderItem(
                product_id=prod.id,
                product_title=prod.title_fa,
                unit_price=unit_price,
                quantity=item.quantity,
                subtotal=subtotal,
            )
        )

    # 3. Fetch and Validate Add-ons
    addons_total = 0
    order_addons_to_create = []
    if payload.addons:
        addon_ids = [a.addon_id for a in payload.addons]
        addon_stmt = select(AddonItem).where(AddonItem.id.in_(addon_ids), AddonItem.is_active == True)
        addon_res = await db.execute(addon_stmt)
        addons_by_id = {a.id: a for a in addon_res.scalars().all()}

        if len(addons_by_id) != len(set(addon_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="برخی از آیتمهای جانبی نامعتبر یا ناموجود هستند",
            )

        for a_input in payload.addons:
            addon = addons_by_id[a_input.addon_id]
            subtotal = addon.price * a_input.quantity
            addons_total += subtotal
            order_addons_to_create.append(
                OrderAddon(
                    addon_id=addon.id,
                    addon_title=addon.title_fa,
                    unit_price=addon.price,
                    quantity=a_input.quantity,
                    subtotal=subtotal,
                )
            )

    # 4. Calculate Delivery Fee
    delivery_fee = (
        0
        if (items_total + addons_total) >= settings.FREE_DELIVERY_THRESHOLD
        else settings.DEFAULT_DELIVERY_FEE
    )
    final_total = items_total + addons_total + delivery_fee

    # 5. Build Order
    tracking_code = generate_tracking_code()
    initial_history = [
        {
            "from_status": None,
            "to_status": OrderStatus.CONFIRMED.value,
            "to_status_fa": STATUS_TITLES_FA[OrderStatus.CONFIRMED],
            "timestamp_jalali": payload.delivery_date_jalali,
            "timestamp_iso": datetime.now(timezone.utc).isoformat(),
            "changed_by": "سیستم سفارش آنلاین",
            "note": "سفارش ثبت و ظرفیت کارگاه گلآرایی رزرو شد.",
        }
    ]

    order = Order(
        tracking_code=tracking_code,
        status=OrderStatus.CONFIRMED,
        customer_id=current_user.id if current_user else None,
        buyer_name=payload.buyer_name,
        buyer_phone=payload.buyer_phone,
        buyer_email=payload.buyer_email,
        recipient_name=payload.recipient_name,
        recipient_phone=payload.recipient_phone,
        recipient_address=payload.recipient_address,
        recipient_city=payload.recipient_city,
        district_zone=payload.district_zone,
        is_surprise=payload.is_surprise,
        greeting_card_message=payload.greeting_card_message,
        greeting_card_sender=payload.greeting_card_sender,
        ribbon_text=payload.ribbon_text,
        delivery_date_jalali=payload.delivery_date_jalali,
        delivery_time_window=payload.delivery_time_window,
        delivery_notes=payload.delivery_notes,
        items_total=items_total,
        addons_total=addons_total,
        delivery_fee=delivery_fee,
        discount_amount=0,
        final_total=final_total,
        status_history=initial_history,
        items=order_items_to_create,
        addons=order_addons_to_create,
    )

    db.add(order)
    await db.commit()

    # Re-fetch order with relations
    stmt = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.addons))
        .where(Order.id == order.id)
    )
    res = await db.execute(stmt)
    full_order = res.scalar_one()
    return full_order


@router.get("/track/{tracking_code}", response_model=PublicOrderTrackOut)
async def track_order_public(tracking_code: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.tracking_code == tracking_code.strip().upper())
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارشی با این کد پیگیری یافت نشد",
        )

    items_titles = [f"{item.product_title} (تعداد: {item.quantity})" for item in order.items]

    return PublicOrderTrackOut(
        tracking_code=order.tracking_code,
        status=order.status,
        status_fa=str(STATUS_TITLES_FA.get(order.status, order.status.value)),
        recipient_name_masked=mask_name(order.recipient_name),
        delivery_date_jalali=order.delivery_date_jalali,
        delivery_time_window=order.delivery_time_window,
        items_summary=items_titles,
        is_surprise=order.is_surprise,
        greeting_card_sender=order.greeting_card_sender,
        arrangement_photo_url=order.arrangement_photo_url,
        timeline=order.status_history or [],
    )


@router.get("/my-orders", response_model=List[OrderListItemOut])
async def get_my_orders(
    current_user: User = Depends(require_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Order)
        .where(Order.customer_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/manage/list", response_model=List[OrderListItemOut])
async def manage_orders_list(
    status_filter: Optional[OrderStatus] = None,
    date_jalali: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Order)
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    if date_jalali:
        stmt = stmt.where(Order.delivery_date_jalali == date_jalali)

    stmt = stmt.order_by(Order.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/manage/{order_id}", response_model=OrderDetailOut)
async def manage_order_detail(
    order_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.addons))
        .where(Order.id == order_id)
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش مورد نظر یافت نشد",
        )
    return order


@router.post("/manage/{order_id}/transition", response_model=OrderDetailOut)
async def transition_order_status(
    order_id: int,
    payload: OrderStatusTransitionRequest,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.addons))
        .where(Order.id == order_id)
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش مورد نظر یافت نشد",
        )

    try:
        apply_order_transition(
            order=order,
            new_status=payload.new_status,
            operator_name=f"{current_user.full_name} ({current_user.role.value})",
            note=payload.note,
            photo_url=payload.photo_url,
        )
    except InvalidStateTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    await db.commit()
    
    # Re-fetch with eager loaded relationships
    stmt = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.addons))
        .where(Order.id == order_id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()
