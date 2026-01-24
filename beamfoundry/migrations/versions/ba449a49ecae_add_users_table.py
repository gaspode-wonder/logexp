"""add users table

Revision ID: ba449a49ecae
Revises: aed4ddd31677
Create Date: 2026-01-18 14:15:21.207435

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ba449a49ecae"
down_revision = "aed4ddd31677"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("users")
