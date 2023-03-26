"""empty message

Revision ID: c38d1b18e04d
Revises: 5a772f2b370d
Create Date: 2023-03-16 10:31:19.767202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c38d1b18e04d'
down_revision = '5a772f2b370d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('global_settings', sa.Column('allow_registrations', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('global_settings', 'allow_registrations')
    # ### end Alembic commands ###