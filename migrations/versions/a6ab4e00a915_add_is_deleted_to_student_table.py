"""Add is_deleted to student table

Revision ID: a6ab4e00a915
Revises: ef8ec6736640
Create Date: 2026-07-10 06:47:41.363181
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a6ab4e00a915"
down_revision = "ef8ec6736640"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("students", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_deleted",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false")
            )
        )


def downgrade():
    with op.batch_alter_table("students", schema=None) as batch_op:
        batch_op.drop_column("is_deleted")