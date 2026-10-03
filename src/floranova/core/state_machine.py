from datetime import datetime, timezone
from typing import Dict, Set, Optional, Tuple
from floranova.models.order import Order, OrderStatus
import jdatetime


# Valid transitions mapping
ALLOWED_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
    OrderStatus.PENDING_PAYMENT: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.ARRANGING, OrderStatus.CANCELLED},
    OrderStatus.ARRANGING: {OrderStatus.QUALITY_APPROVED, OrderStatus.CANCELLED},
    OrderStatus.QUALITY_APPROVED: {OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED},
    OrderStatus.OUT_FOR_DELIVERY: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}

STATUS_TITLES_FA: Dict[OrderStatus, str] = {
    OrderStatus.PENDING_PAYMENT: "در انتظار پرداخت",
    OrderStatus.CONFIRMED: "تایید سفارش و رزرو گل",
    OrderStatus.ARRANGING: "در حال گلآرایی در آتلیه",
    OrderStatus.QUALITY_APPROVED: "تایید کنترل کیفی گلها",
    OrderStatus.OUT_FOR_DELIVERY: "تحویل به سفیر اختصاصی",
    OrderStatus.DELIVERED: "تحویل نهایی به گیرنده",
    OrderStatus.CANCELLED: "لغو شده",
}


class InvalidStateTransitionError(Exception):
    def __init__(self, current: OrderStatus, target: OrderStatus):
        self.current = current
        self.target = target
        super().__init__(
            f"امکان تغییر وضعیت از '{STATUS_TITLES_FA.get(current, current.value)}' به "
            f"'{STATUS_TITLES_FA.get(target, target.value)}' وجود ندارد."
        )


def can_transition(current: OrderStatus, target: OrderStatus) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def apply_order_transition(
    order: Order,
    new_status: OrderStatus,
    operator_name: str = "سیستم",
    note: Optional[str] = None,
    photo_url: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    if not can_transition(order.status, new_status):
        raise InvalidStateTransitionError(order.status, new_status)

    old_status = order.status
    order.status = new_status
    if photo_url:
        order.arrangement_photo_url = photo_url

    # Record history entry
    now_j = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    history_entry = {
        "from_status": old_status.value,
        "to_status": new_status.value,
        "to_status_fa": STATUS_TITLES_FA.get(new_status, new_status.value),
        "timestamp_jalali": now_j,
        "timestamp_iso": datetime.now(timezone.utc).isoformat(),
        "changed_by": operator_name,
        "note": note or f"تغییر وضعیت به {STATUS_TITLES_FA.get(new_status, new_status.value)}",
    }
    
    # Update status history
    current_history = list(order.status_history or [])
    current_history.append(history_entry)
    order.status_history = current_history
    order.updated_at = datetime.now(timezone.utc)

    return True, None
