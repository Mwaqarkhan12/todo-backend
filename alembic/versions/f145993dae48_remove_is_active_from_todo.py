"""remove is_active from todo

Revision ID: f145993dae48
Revises: b5e3126c249e
Create Date: 2026-08-18 21:13:42.437619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f145993dae48'
down_revision: Union[str, Sequence[str], None] = 'b5e3126c249e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
