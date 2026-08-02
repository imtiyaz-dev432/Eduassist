"""Allow teacher password to be nullable

Revision ID: 2c8c53b92f3a
Revises: 59f7515f2f60
Create Date: 2026-07-30 13:43:11.986540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c8c53b92f3a'
down_revision = '59f7515f2f60'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('teachers', schema=None) as batch_op:
        batch_op.alter_column(
            'password',
            existing_type=sa.VARCHAR(length=260),
            nullable=True
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('teachers', schema=None) as batch_op:
        batch_op.alter_column(
            'password',
            existing_type=sa.VARCHAR(length=260),
            nullable=False
        )

    # ### end Alembic commands ###
