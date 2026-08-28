"""v2 squash — treatment_plan initial.

Initial schema for the `treatment_plan` module.

Revision ID: ae_0001
Revises:
Create Date: 2026-04-21

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "ae_0001"
down_revision: str | None = "ag_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "aesthetic_plans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("clinic_id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("plan_number", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("budget_id", sa.UUID(), nullable=True),
        sa.Column("assigned_professional_id", sa.UUID(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("diagnosis_notes", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assigned_professional_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["budget_id"],
            ["budgets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["clinic_id"],
            ["clinics.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("clinic_id", "plan_number", name="uq_treatment_plan_number"),
    )
    op.create_index("idx_aesthetic_plans_budget", "aesthetic_plans", ["budget_id"], unique=False)
    op.create_index("idx_aesthetic_plans_patient", "aesthetic_plans", ["patient_id"], unique=False)
    op.create_index(
        "idx_aesthetic_plans_status", "aesthetic_plans", ["clinic_id", "status"], unique=False
    )
    op.create_index(
        op.f("ix_aesthetic_plans_budget_id"), "aesthetic_plans", ["budget_id"], unique=True
    )
    op.create_index(
        op.f("ix_aesthetic_plans_clinic_id"), "aesthetic_plans", ["clinic_id"], unique=False
    )
    op.create_index(
        op.f("ix_aesthetic_plans_patient_id"), "aesthetic_plans", ["patient_id"], unique=False
    )

    op.create_table(
        "aesthetic_plan_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("clinic_id", sa.UUID(), nullable=False),
        sa.Column("treatment_plan_id", sa.UUID(), nullable=False),
        sa.Column("treatment_id", sa.UUID(), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("completed_without_appointment", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_by", sa.UUID(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["clinic_id"],
            ["clinics.id"],
        ),
        sa.ForeignKeyConstraint(
            ["completed_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(["treatment_id"], ["treatments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["treatment_plan_id"], ["aesthetic_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("treatment_id", name="uq_planned_item_treatment"),
    )
    op.create_index(
        "idx_planned_items_plan", "aesthetic_plan_items", ["treatment_plan_id"], unique=False
    )
    op.create_index(
        "idx_planned_items_status",
        "aesthetic_plan_items",
        ["treatment_plan_id", "status"],
        unique=False,
    )
    op.create_index(
        "idx_planned_items_treatment", "aesthetic_plan_items", ["treatment_id"], unique=False
    )
    op.create_index(
        op.f("ix_aesthetic_plan_items_clinic_id"),
        "aesthetic_plan_items",
        ["clinic_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_aesthetic_plan_items_treatment_id"),
        "aesthetic_plan_items",
        ["treatment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_aesthetic_plan_items_treatment_plan_id"),
        "aesthetic_plan_items",
        ["treatment_plan_id"],
        unique=False,
    )

    op.create_table(
        "treatment_media",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("clinic_id", sa.UUID(), nullable=False),
        sa.Column("planned_treatment_item_id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["clinic_id"],
            ["clinics.id"],
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["planned_treatment_item_id"], ["aesthetic_plan_items.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_treatment_media_document", "treatment_media", ["document_id"], unique=False
    )
    op.create_index(
        "idx_treatment_media_item", "treatment_media", ["planned_treatment_item_id"], unique=False
    )
    op.create_index(
        op.f("ix_treatment_media_clinic_id"), "treatment_media", ["clinic_id"], unique=False
    )
    op.create_index(
        op.f("ix_treatment_media_document_id"), "treatment_media", ["document_id"], unique=False
    )
    op.create_index(
        op.f("ix_treatment_media_planned_treatment_item_id"),
        "treatment_media",
        ["planned_treatment_item_id"],
        unique=False,
    )

    # Deferred FK from agenda.appointment_treatments → aesthetic_plan_items.
    # agenda.ag_0001 creates the column but skips the constraint to break
    # the circular module dependency (agenda depends on treatment_plan and
    # vice versa).
    op.create_foreign_key(
        "fk_appointment_treatments_planned_item",
        "appointment_treatments",
        "aesthetic_plan_items",
        ["planned_treatment_item_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_appointment_treatments_planned_item",
        "appointment_treatments",
        type_="foreignkey",
    )
    op.drop_table("treatment_media")
    op.drop_table("aesthetic_plan_items")
    op.drop_table("aesthetic_plans")
