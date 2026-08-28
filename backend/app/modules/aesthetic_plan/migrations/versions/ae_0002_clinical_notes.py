"""Clinical notes + polymorphic note attachments.

In the Otomedis estetic fork this revision is a NO-OP: the
``clinical_notes`` / ``clinical_note_attachments`` tables are created and
owned by the ``clinical_notes`` module (via treatment_plan.tp_0002 →
clinical_notes.cn_0001), which runs in this fork too because the module
directories are still on disk. Duplicating the CREATE here would fail
with a duplicate-table error when both branches run.

Revision ID: ae_0002
Revises: ae_0001
Create Date: 2026-04-24

"""

from collections.abc import Sequence

from alembic import op

revision: str = "ae_0002"
down_revision: str | None = "ae_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # No-op — see module docstring. clinical_notes tables are owned by the
    # clinical_notes module / treatment_plan.tp_0002 chain.
    pass


def downgrade() -> None:
    # No-op — nothing was created by this revision.
    pass
