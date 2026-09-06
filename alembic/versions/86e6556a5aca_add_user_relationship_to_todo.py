"""add user relationship to todo

Revision ID: 86e6556a5aca
Revises:
Create Date: 2026-08-14 20:05:44.541467

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "86e6556a5aca"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add user_id temporarily as nullable
    op.add_column(
        "todo",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    # 2. Get an existing user
    connection = op.get_bind()

    user = connection.execute(
        sa.text('SELECT id FROM "user" ORDER BY id LIMIT 1')
    ).fetchone()

    if user is None:
        raise RuntimeError(
            "No users exist in the user table. "
            "Create a user before running this migration."
        )

    user_id = user[0]

    # 3. Assign all existing Todos to the first user
    connection.execute(
        sa.text("UPDATE todo SET user_id = :user_id"),
        {"user_id": user_id},
    )

    # 4. Make user_id required
    op.alter_column(
        "todo",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # 5. Create the foreign key
    op.create_foreign_key(
        "fk_todo_user_id_user",
        "todo",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_todo_user_id_user",
        "todo",
        type_="foreignkey",
    )

    op.drop_column("todo", "user_id")