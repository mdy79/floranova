from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from floranova.models.order import OrderStatus


class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1, le=50)


class OrderAddonInput(BaseModel):
    addon_id: int
    quantity: int = Field(1, ge=1, le=50)


class CheckoutRequest(BaseModel):
    buyer_name: str = Field(..., min_length=2, max_length=128)
    buyer_phone: str = Field(..., pattern=r"^09[0-9]{9}$")
    buyer_email: Optional[str] = None
    
    recipient_name: str = Field(..., min_length=2, max_length=128)
    recipient_phone: str = Field(..., pattern=r"^09[0-9]{9}$")
    recipient_address: str = Field(..., min_length=5)
    recipient_city: str = Field("تهران", max_length=64)
    district_zone: Optional[str] = None
    
    is_surprise: bool = False
    greeting_card_message: Optional[str] = None
    greeting_card_sender: Optional[str] = None
    ribbon_text: Optional[str] = None
    
    delivery_date_jalali: str = Field(..., pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    delivery_time_window: str = Field(..., min_length=3, max_length=64)
    delivery_notes: Optional[str] = None
    
    items: List[OrderItemInput] = Field(..., min_length=1)
    addons: List[OrderAddonInput] = Field(default_factory=list)


class OrderStatusTransitionRequest(BaseModel):
    new_status: OrderStatus
    note: Optional[str] = None
    photo_url: Optional[str] = None


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_title: str
    unit_price: int
    quantity: int
    subtotal: int


class OrderAddonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    addon_id: int
    addon_title: str
    unit_price: int
    quantity: int
    subtotal: int


class OrderListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tracking_code: str
    status: OrderStatus
    buyer_name: str
    recipient_name: str
    delivery_date_jalali: str
    delivery_time_window: str
    is_surprise: bool
    final_total: int
    created_at: datetime


class OrderDetailOut(OrderListItemOut):
    model_config = ConfigDict(from_attributes=True)

    buyer_phone: str
    buyer_email: Optional[str]
    recipient_phone: str
    recipient_address: str
    recipient_city: str
    district_zone: Optional[str]
    greeting_card_message: Optional[str]
    greeting_card_sender: Optional[str]
    ribbon_text: Optional[str]
    delivery_notes: Optional[str]
    items_total: int
    addons_total: int
    delivery_fee: int
    discount_amount: int
    arrangement_photo_url: Optional[str]
    status_history: List[Dict[str, Any]]
    items: List[OrderItemOut]
    addons: List[OrderAddonOut]


class PublicOrderTrackOut(BaseModel):
    tracking_code: str
    status: OrderStatus
    status_fa: str
    recipient_name_masked: str
    delivery_date_jalali: str
    delivery_time_window: str
    items_summary: List[str]
    is_surprise: bool
    greeting_card_sender: Optional[str]
    arrangement_photo_url: Optional[str]
    timeline: List[Dict[str, Any]]


class AdminStatsOut(BaseModel):
    total_revenue_toman: int
    today_orders_count: int
    active_arranging_count: int
    out_for_delivery_count: int
    delivered_count: int
    pending_count: int
    active_fresh_stems: int
    spoilage_risk_percent: float
