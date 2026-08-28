"""Add assigned_professional_id to aesthetic_plan_items.

Each line in a treatment plan can now record which professional is
responsible for performing that specific treatment. Backfills existing
items with the doctor of their parent plan so the data starts in a
consistent state.

Revision ID: ae_0005
Revises: ae_0004
Create Date: 2026-05-18

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "ae_0005"
down_revision: str | None = "ae_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "aesthetic_plan_items",
        sa.Column("assigned_professional_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_aesthetic_plan_items_assigned_professional",
        "aesthetic_plan_items",
        "users",
        ["assigned_professional_id"],
        ["id"],
    )
    op.create_index(
        "ix_aesthetic_plan_items_assigned_professional_id",
        "aesthetic_plan_items",
        ["assigned_professional_id"],
    )
    op.create_index(
        "idx_aesthetic_plan_items_plan_professional",
        "aesthetic_plan_items",
        ["treatment_plan_id", "assigned_professional_id"],
    )

    # Backfill from the parent plan's assigned_professional_id. We populate
    # every item (including completed ones) so historical queries have a
    # consistent value; the UI keeps showing completed_by for completed items.
    op.execute(
        """
        UPDATE aesthetic_plan_items pti
           SET assigned_professional_id = tp.assigned_professional_id
          FROM aesthetic_plans tp
         WHERE pti.treatment_plan_id = tp.id
           AND pti.assigned_professional_id IS NULL
           AND tp.assigned_professional_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_index(
        "idx_aesthetic_plan_items_plan_professional",
        table_name="aesthetic_plan_items",
    )
    op.drop_index(
        "ix_aesthetic_plan_items_assigned_professional_id",
        table_name="aesthetic_plan_items",
    )
    op.drop_constraint(
        "fk_aesthetic_plan_items_assigned_professional",
        "aesthetic_plan_items",
        type_="foreignkey",
    )
    op.drop_column("aesthetic_plan_items", "assigned_professional_id")
