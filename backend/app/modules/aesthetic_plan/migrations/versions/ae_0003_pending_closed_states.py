"""Plan workflow rework — add pending and closed states.

Adds metadata to support the pending → active | closed pipeline:

- ``closure_reason`` / ``closure_note`` / ``closed_at`` — populated on
  transition to terminal ``closed`` state.
- ``confirmed_at`` — set when the doctor confirms the plan
  (``draft`` → ``pending``).

Migrates any pre-existing ``status='cancelled'`` rows to
``status='closed'`` with ``closure_reason='cancelled_by_clinic'`` since
the new state machine no longer recognises ``cancelled``. The app is
not yet in production so no defensive backfill is needed beyond this.

Revision ID: ae_0003
Revises: ae_0002
Create Date: 2026-04-28

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "ae_0003"
down_revision: str | None = "ae_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "aesthetic_plans",
        sa.Column("closure_reason", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "aesthetic_plans",
        sa.Column("closure_note", sa.Text(), nullable=True),
    )
    op.add_column(
        "aesthetic_plans",
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "aesthetic_plans",
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "idx_aesthetic_plans_clinic_status_closed",
        "aesthetic_plans",
        ["clinic_id", "status", "closed_at"],
    )

    # Migrate retired ``cancelled`` rows to the new terminal state.
    op.execute(
        """
        UPDATE aesthetic_plans
        SET status = 'closed',
            closure_reason = 'cancelled_by_clinic',
            closed_at = COALESCE(updated_at, NOW())
        WHERE status = 'cancelled'
        """
    )


def downgrade() -> None:
    # Revert closed-with-cancelled_by_clinic rows back to ``cancelled``
    # so the legacy state machine still works after rollback.
    op.execute(
        """
        UPDATE aesthetic_plans
        SET status = 'cancelled',
            closure_reason = NULL,
            closed_at = NULL
        WHERE status = 'closed' AND closure_reason = 'cancelled_by_clinic'
        """
    )

    op.drop_index(
        "idx_aesthetic_plans_clinic_status_closed",
        table_name="aesthetic_plans",
    )
    op.drop_column("aesthetic_plans", "confirmed_at")
    op.drop_column("aesthetic_plans", "closed_at")
    op.drop_column("aesthetic_plans", "closure_note")
    op.drop_column("aesthetic_plans", "closure_reason")
