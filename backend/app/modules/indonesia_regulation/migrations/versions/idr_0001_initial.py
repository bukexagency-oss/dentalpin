"""indonesia_regulation — initial schema.

NPWP & PPN registration settings per clinic, plus e-invoice (Faktur Pajak)
submission tracking.

Revision ID: idr_0001
Revises: 0001
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "idr_0001"
# Chain off the core init (mirrors verifactu/india_gst pattern).
# ``removable=True`` — a ``alembic downgrade indonesia_regulation@base``
# walks only indonesia_regulation revisions on uninstall.
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = ("indonesia_regulation",)
depends_on: str | Sequence[str] | None = "bil_0001"


def upgrade() -> None:
    op.create_table(
        "indonesia_regulation_settings",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("clinic_id", UUID(as_uuid=True), nullable=False),
        sa.Column("npwp", sa.String(20), nullable=True),
        sa.Column("trade_name", sa.String(200), nullable=True),
        sa.Column("registration_type", sa.String(20), nullable=False, server_default="non_pkp"),
        sa.Column("ppn_rate", sa.String(10), nullable=False, server_default="ppn_11"),
        sa.Column("clinic_province", sa.String(2), nullable=True),
        sa.Column("show_npwp_on_invoice", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("show_ppn_on_invoice", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("bpjs_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("bpjs_faskes_tk", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("clinic_id", name="uq_indonesia_regulation_settings_clinic"),
        sa.CheckConstraint(
            "registration_type IN ('pengusaha_kena_pajak', 'non_pkp', 'exempt')",
            name="ck_indonesia_regulation_settings_registration_type",
        ),
        sa.ForeignKeyConstraint(
            ["clinic_id"], ["clinics.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_indonesia_regulation_settings_clinic_id",
        "indonesia_regulation_settings",
        ["clinic_id"],
    )

    op.create_table(
        "indonesia_regulation_einvoice_submissions",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("clinic_id", UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", UUID(as_uuid=True), nullable=False),
        sa.Column("state", sa.String(20), nullable=False, server_default="not_configured"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("faktur_pajak_number", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_id", name="uq_indonesia_regulation_einvoice_invoice"),
        sa.ForeignKeyConstraint(
            ["clinic_id"], ["clinics.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id"], ["invoices.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_indonesia_regulation_einvoice_clinic_id",
        "indonesia_regulation_einvoice_submissions",
        ["clinic_id"],
    )


def downgrade() -> None:
    op.drop_table("indonesia_regulation_einvoice_submissions")
    op.drop_table("indonesia_regulation_settings")