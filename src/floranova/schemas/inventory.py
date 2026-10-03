from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from floranova.models.inventory import FreshnessStatus


class BatchCreate(BaseModel):
    batch_code: str = Field(..., min_length=3, max_length=64)
    flower_species: str = Field(..., min_length=2, max_length=128)
    stems_received: int = Field(..., gt=0)
    stems_remaining: int = Field(..., ge=0)
    unit_cost_toman: int = Field(..., gt=0)
    max_freshness_days: int = Field(6, ge=1, le=30)
    notes: Optional[str] = None


class BatchUpdate(BaseModel):
    stems_remaining: Optional[int] = Field(None, ge=0)
    status: Optional[FreshnessStatus] = None
    notes: Optional[str] = None


class BatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_code: str
    flower_species: str
    stems_received: int
    stems_remaining: int
    unit_cost_toman: int
    received_date: datetime
    max_freshness_days: int
    status: FreshnessStatus
    notes: Optional[str]
    updated_at: datetime


class InventorySummaryOut(BaseModel):
    total_stems_fresh: int
    total_stems_rotating: int
    total_stems_wasted: int
    active_batches_count: int
    spoilage_risk_percentage: float
