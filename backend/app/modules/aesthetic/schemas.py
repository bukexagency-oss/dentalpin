"""Pydantic schemas for the aesthetic module.

CRUD schemas for PhotoJourney, ConsultationNote, TreatmentHistory and
ProductRecommendation. ``clinic_id`` is never client-supplied — the
service layer stamps it from the authenticated clinic context.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# --- PhotoJourney ---------------------------------------------------------


class PhotoJourneyCreate(BaseModel):
    patient_id: UUID
    photo_type: str = Field(min_length=1, max_length=50)  # before, after, progress
    photo_url: str = Field(min_length=1, max_length=500)
    notes: str | None = None
    taken_at: datetime | None = None


class PhotoJourneyUpdate(BaseModel):
    photo_type: str | None = Field(default=None, min_length=1, max_length=50)
    photo_url: str | None = Field(default=None, min_length=1, max_length=500)
    notes: str | None = None
    taken_at: datetime | None = None


class PhotoJourneyResponse(BaseModel):
    id: UUID
    clinic_id: UUID
    patient_id: UUID
    photo_type: str
    photo_url: str
    notes: str | None
    taken_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- ConsultationNote -----------------------------------------------------


class ConsultationNoteCreate(BaseModel):
    patient_id: UUID
    consultation_type: str = Field(min_length=1, max_length=50)  # initial, follow_up, review
    findings: str | None = None
    recommendations: str | None = None
    skin_analysis: str | None = None


class ConsultationNoteUpdate(BaseModel):
    consultation_type: str | None = Field(default=None, min_length=1, max_length=50)
    findings: str | None = None
    recommendations: str | None = None
    skin_analysis: str | None = None


class ConsultationNoteResponse(BaseModel):
    id: UUID
    clinic_id: UUID
    patient_id: UUID
    consultation_type: str
    findings: str | None
    recommendations: str | None
    skin_analysis: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- TreatmentHistory -----------------------------------------------------


class TreatmentHistoryCreate(BaseModel):
    patient_id: UUID
    treatment_type: str = Field(min_length=1, max_length=100)
    product_used: str | None = Field(default=None, max_length=200)
    dosage_cc: float | None = Field(default=None, ge=0)
    area_treated: str | None = Field(default=None, max_length=200)
    notes: str | None = None
    performed_at: datetime | None = None


class TreatmentHistoryUpdate(BaseModel):
    treatment_type: str | None = Field(default=None, min_length=1, max_length=100)
    product_used: str | None = Field(default=None, max_length=200)
    dosage_cc: float | None = Field(default=None, ge=0)
    area_treated: str | None = Field(default=None, max_length=200)
    notes: str | None = None
    performed_at: datetime | None = None


class TreatmentHistoryResponse(BaseModel):
    id: UUID
    clinic_id: UUID
    patient_id: UUID
    treatment_type: str
    product_used: str | None
    dosage_cc: float | None
    area_treated: str | None
    notes: str | None
    performed_by: UUID
    performed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- ProductRecommendation ------------------------------------------------


class ProductRecommendationCreate(BaseModel):
    patient_id: UUID
    product_name: str = Field(min_length=1, max_length=200)
    product_type: str = Field(min_length=1, max_length=50)
    usage_instructions: str | None = None
    frequency: str | None = Field(default=None, max_length=100)
    duration_days: int | None = Field(default=None, ge=1)


class ProductRecommendationUpdate(BaseModel):
    product_name: str | None = Field(default=None, min_length=1, max_length=200)
    product_type: str | None = Field(default=None, min_length=1, max_length=50)
    usage_instructions: str | None = None
    frequency: str | None = Field(default=None, max_length=100)
    duration_days: int | None = Field(default=None, ge=1)


class ProductRecommendationResponse(BaseModel):
    id: UUID
    clinic_id: UUID
    patient_id: UUID
    product_name: str
    product_type: str
    usage_instructions: str | None
    frequency: str | None
    duration_days: int | None
    prescribed_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
