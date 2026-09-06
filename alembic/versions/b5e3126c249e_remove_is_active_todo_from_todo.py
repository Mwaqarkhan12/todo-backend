"""remove is_active_todo from todo

Revision ID: b5e3126c249e
Revises: 7379627cd940
Create Date: 2026-08-18 21:13:17.073240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5e3126c249e'
down_revision: Union[str, Sequence[str], None] = '7379627cd940'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
