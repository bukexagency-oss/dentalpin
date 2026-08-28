"""Move treatment_media → media.media_attachments + tag documents.

In the Otomedis estetic fork this revision is a NO-OP: the data migration
from treatment_media → media_attachments is handled by the
treatment_plan.tp_0004 migration (which also runs in this fork). Because
the estetic fork has a fresh DB with no legacy treatment_media data,
duplicating this migration would fail with a missing-table error when
tp_0004 runs first (or vice versa).

Revision ID: ae_0004
Revises: ae_0003
Create Date: 2026-05-02

"""

from collections.abc import Sequence

from alembic import op

revision: str = "ae_0004"
down_revision: str | None = "ae_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = ("med_0002",)


def upgrade() -> None:
    # No-op — see module docstring. The treatment_media → media migration
    # is handled by treatment_plan.tp_0004.
    pass


def downgrade() -> None:
    # No-op — nothing was created by this revision.
    pass