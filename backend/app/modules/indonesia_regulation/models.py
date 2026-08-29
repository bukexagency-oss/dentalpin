"""Indonesia regulation models — NPWP, PPN, and e-invoice (Faktur Pajak)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class IndonesiaRegulationSettings(Base):
    """Per-clinic NPWP / PPN registration settings for Indonesia."""

    __tablename__ = "indonesia_regulation_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    npwp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    trade_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    registration_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="non_pkp"
    )
    ppn_rate: Mapped[str] = mapped_column(String(10), nullable=False, default="ppn_11")
    clinic_province: Mapped[str | None] = mapped_column(String(2), nullable=True)
    show_npwp_on_invoice: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    show_ppn_on_invoice: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    bpjs_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    bpjs_faskes_tk: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("clinic_id", name="uq_indonesia_regulation_settings_clinic"),
        CheckConstraint(
            "registration_type IN ('pengusaha_kena_pajak', 'non_pkp', 'exempt')",
            name="ck_indonesia_regulation_settings_registration_type",
        ),
    )


class IndonesiaRegulationEInvoiceSubmission(Base):
    """Tracks e-invoice (Faktur Pajak) submission lifecycle per invoice."""

    __tablename__ = "indonesia_regulation_einvoice_submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False
    )
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="not_configured")
    error_message: Mapped[str | None] = mapped_column(nullable=True)
    faktur_pajak_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("invoice_id", name="uq_indonesia_regulation_einvoice_invoice"),
    )