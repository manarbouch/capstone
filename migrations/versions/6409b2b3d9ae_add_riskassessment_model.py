"""Add RiskAssessment model

Revision ID: 6409b2b3d9ae
Revises: b085b88ac6ed
Create Date: 2024-11-27 10:04:53.850315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6409b2b3d9ae'
down_revision = 'b085b88ac6ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('risk_assessments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('goal', sa.String(length=50), nullable=False),
    sa.Column('time_horizon', sa.String(length=50), nullable=False),
    sa.Column('reaction', sa.String(length=50), nullable=False),
    sa.Column('savings_rate', sa.String(length=50), nullable=False),
    sa.Column('experience', sa.String(length=50), nullable=False),
    sa.Column('risk_score', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('risk_assessments')
    # ### end Alembic commands ###