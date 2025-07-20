"""add notification table

Revision ID: f1e1f099a4d0
Revises: 
Create Date: 2025-07-20 19:57:44.332131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1e1f099a4d0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Only create the notification table and its constraints
    op.create_table(
        'notification',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False, default="normal"),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('channel', sa.String(), nullable=False, default="in_app"),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('ix_public_notification_user_id', 'notification', ['user_id'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_public_notification_user_id', table_name='notification')
    op.drop_table('notification')
