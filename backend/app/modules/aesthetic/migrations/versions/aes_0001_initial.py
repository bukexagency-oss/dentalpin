"""aesthetic — initial.

Owns the ``photo_journeys``, ``consultation_notes``, ``treatment_histories``
and ``product_recommendations`` tables for the Otomedis esthetic clinic
fork. Chained off the patients branch (``pat_0003``) because every table
has a patient_id FK. Sits on its own Alembic branch (``branch_labels=(
"aesthetic",)``) per ADR 0002 / issue #56.

Revision ID: aes_0001
Revises: pat_0003
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "aes_0001"
down_revision: str | None = "pat_0003"
branch_labels: str | Sequence[str] | None = ("aesthetic",)
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "photo_journeys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("clinic_id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("photo_type", sa.String(length=50), nullable=False),
        sa.Column("photo_url", sa.String(length=500), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_photo_journeys_clinic_id"), "photo_journeys", ["clinic_id"], unique=False
    )
    op.create_index(
        op.f("ix_photo_journeys_patient_id"), "photo_journeys", ["patient_id"], unique=False
    )

    op.create_table(
        "consultation_notes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("clinic_id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("consultation_type", sa.String(length=50), nullable=False),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.Text(), nullable=True),
        sa.Column("skin_analysis", sa.Text(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_consultation_notes_clinic_id"),
        "consultation_notes",
        ["clinic_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_consultation_notes_patient_id"),
        "consultation_notes",
        ["patient_id"],
        unique=False,
    )

    op.create_table(
        "treatment_histories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("clinic_id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("treatment_type", sa.String(length=100), nullable=False),
        sa.Column("product_used", sa.String(length=200), nullable=True),
        sa.Column("dosage_cc", sa.Float(), nullable=True),
        sa.Column("area_treated", sa.String(length=200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.UUID(), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_treatment_histories_clinic_id"),
        "treatment_histories",
        ["clinic_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_treatment_histories_patient_id"),
        "treatment_histories",
        ["patient_id"],
        unique=False,
    )

    op.create_table(
        "product_recommendations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("clinic_id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("product_type", sa.String(length=50), nullable=False),
        sa.Column("usage_instructions", sa.Text(), nullable=True),
        sa.Column("frequency", sa.String(length=100), nullable=True),
        sa.Column("duration_days", sa.Integer(), nullable=True),
        sa.Column("prescribed_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["clinic_id"], ["clinics.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["prescribed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_product_recommendations_clinic_id"),
        "product_recommendations",
        ["clinic_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_product_recommendations_patient_id"),
        "product_recommendations",
        ["patient_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_product_recommendations_patient_id"), table_name="product_recommendations"
    )
    op.drop_index(
        op.f("ix_product_recommendations_clinic_id"), table_name="product_recommendations"
    )
    op.drop_table("product_recommendations")

    op.drop_index(
        op.f("ix_treatment_histories_patient_id"), table_name="treatment_histories"
    )
    op.drop_index(op.f("ix_treatment_histories_clinic_id"), table_name="treatment_histories")
    op.drop_table("treatment_histories")

    op.drop_index(op.f("ix_consultation_notes_patient_id"), table_name="consultation_notes")
    op.drop_index(op.f("ix_consultation_notes_clinic_id"), table_name="consultation_notes")
    op.drop_table("consultation_notes")

    op.drop_index(op.f("ix_photo_journeys_patient_id"), table_name="photo_journeys")
    op.drop_index(op.f("ix_photo_journeys_clinic_id"), table_name="photo_journeys")
    op.drop_table("photo_journeys")
