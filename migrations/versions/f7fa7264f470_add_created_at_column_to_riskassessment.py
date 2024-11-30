""""Add created_at column to RiskAssessment

Revision ID: f7fa7264f470
Revises: 6409b2b3d9ae
Create Date: 2024-11-27 16:21:47.294727
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7fa7264f470'
down_revision = '6409b2b3d9ae'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'created_at' column to RiskAssessment table
    op.add_column('risk_assessment', sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()))


def downgrade():
    # Remove 'created_at' column if needed (for rollback)
    op.drop_column('risk_assessment', 'created_at')
