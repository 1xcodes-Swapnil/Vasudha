"""Create environmental_profiles table.

Revision ID: 001_env_profiles
Revises: 
Create Date: 2026-09-16 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_env_profiles'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'environmental_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('region', sa.String(length=128), nullable=True),
        sa.Column('ecosystem', sa.String(length=128), nullable=True),
        sa.Column('state_data', sa.JSON(), nullable=False),
        sa.Column('metrics_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_env_profiles_name', 'environmental_profiles', ['name'])
    op.create_index('ix_env_profiles_latitude', 'environmental_profiles', ['latitude'])
    op.create_index('ix_env_profiles_longitude', 'environmental_profiles', ['longitude'])
    op.create_index('ix_env_profiles_region', 'environmental_profiles', ['region'])
    op.create_index('ix_env_profiles_ecosystem', 'environmental_profiles', ['ecosystem'])


def downgrade() -> None:
    op.drop_index('ix_env_profiles_ecosystem', table_name='environmental_profiles')
    op.drop_index('ix_env_profiles_region', table_name='environmental_profiles')
    op.drop_index('ix_env_profiles_longitude', table_name='environmental_profiles')
    op.drop_index('ix_env_profiles_latitude', table_name='environmental_profiles')
    op.drop_index('ix_env_profiles_name', table_name='environmental_profiles')
    op.drop_table('environmental_profiles')
