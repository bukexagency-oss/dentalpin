"""Aesthetic module database models.

PhotoJourney, ConsultationNote, TreatmentHistory, and ProductRecommendation
tables for the esthetic clinic workflow. Every multi-tenant table has a
clinic_id FK with an index.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.core.auth.models import Clinic, User
    from app.modules.patients.models import Patient


class PhotoJourney(Base, TimestampMixin):
    """Before/after photos per patient."""

    __tablename__ = "photo_journeys"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    clinic_id: Mapped[UUID] = mapped_column(ForeignKey("clinics.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), index=True)

    photo_type: Mapped[str] = mapped_column(String(50))  # before, after, progress
    photo_url: Mapped[str] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    clinic: Mapped["Clinic"] = relationship()
    patient: Mapped["Patient"] = relationship()


class ConsultationNote(Base, TimestampMixin):
    """Consultation notes per patient."""

    __tablename__ = "consultation_notes"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    clinic_id: Mapped[UUID] = mapped_column(ForeignKey("clinics.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), index=True)

    consultation_type: Mapped[str] = mapped_column(String(50))  # initial, follow_up, review
    findings: Mapped[str | None] = mapped_column(Text)
    recommendations: Mapped[str | None] = mapped_column(Text)
    skin_analysis: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Relationships
    clinic: Mapped["Clinic"] = relationship()
    patient: Mapped["Patient"] = relationship()
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])


class TreatmentHistory(Base, TimestampMixin):
    """Per-patient treatment record."""

    __tablename__ = "treatment_histories"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    clinic_id: Mapped[UUID] = mapped_column(ForeignKey("clinics.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), index=True)

    treatment_type: Mapped[str] = mapped_column(String(100))  # e.g. botox, filler, peel
    product_used: Mapped[str | None] = mapped_column(String(200))
    dosage_cc: Mapped[float | None] = mapped_column(Float)  # dosage in cc
    area_treated: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    performed_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    performed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    clinic: Mapped["Clinic"] = relationship()
    patient: Mapped["Patient"] = relationship()
    performer: Mapped["User"] = relationship(foreign_keys=[performed_by])


class ProductRecommendation(Base, TimestampMixin):
    """Skincare post-treatment recommendations."""

    __tablename__ = "product_recommendations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    clinic_id: Mapped[UUID] = mapped_column(ForeignKey("clinics.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), index=True)

    product_name: Mapped[str] = mapped_column(String(200))
    product_type: Mapped[str] = mapped_column(String(50))  # cleanser, moisturizer, spf, serum
    usage_instructions: Mapped[str | None] = mapped_column(Text)
    frequency: Mapped[str | None] = mapped_column(String(100))  # e.g. twice daily, nightly
    duration_days: Mapped[int | None] = mapped_column(Integer)
    prescribed_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Relationships
    clinic: Mapped["Clinic"] = relationship()
    patient: Mapped["Patient"] = relationship()
    prescriber: Mapped["User"] = relationship(foreign_keys=[prescribed_by])