"""init users (manual)

Revision ID: 0001_init_users
Revises: 
Create Date: 2025-10-13

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '0001_init_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')


