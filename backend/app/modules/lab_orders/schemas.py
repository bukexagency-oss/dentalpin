"""Pydantic schemas for lab_orders."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

WorkType = Literal[
    "skin_test", "patch_test", "allergy_test", "custom_skincare",
    "splint", "phlebotomy", "culture_swab", "other"
]
OrderStatus = Literal["sent", "in_progress", "ready", "received", "cancelled"]
ImpressionType = Literal["skin_swab", "blood_sample", "culture", "photography", "other"]
ShadeSelection = Literal[
    "porcelain", "ivory", "fair", "light", "light_medium", "medium",
    "medium_tan", "tan", "deep", "rich_deep", "custom", "other"
]


class LabOrderCreate(BaseModel):
    patient_id: UUID
    lab_contact_id: UUID
    work_type: WorkType
    tooth_reference: str | None = Field(default=None, max_length=50)
    impression_type: ImpressionType | None = None
    antagonist_info: str | None = Field(default=None, max_length=500)
    shade: ShadeSelection | None = None
    sent_date: date
    expected_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class LabOrderUpdate(BaseModel):
    lab_contact_id: UUID | None = None
    work_type: WorkType | None = None
    tooth_reference: str | None = Field(default=None, max_length=50)
    impression_type: ImpressionType | None = None
    antagonist_info: str | None = Field(default=None, max_length=500)
    shade: ShadeSelection | None = None
    status: OrderStatus | None = None
    expected_date: date | None = None
    received_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class LabOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    clinic_id: UUID
    patient_id: UUID
    patient_name: str
    lab_contact_id: UUID
    lab_contact_name: str
    work_type: WorkType
    tooth_reference: str | None
    impression_type: ImpressionType | None
    antagonist_info: str | None
    shade: ShadeSelection | None
    status: OrderStatus
    sent_date: date
    expected_date: date | None
    received_date: date | None
    notes: str | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
