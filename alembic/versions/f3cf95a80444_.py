"""empty message

Revision ID: f3cf95a80444
Revises: 702abfef734b
Create Date: 2023-02-21 21:28:18.301566

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f3cf95a80444'
down_revision = '702abfef734b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mail_bounce_status',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('from_address', sa.String(length=255), nullable=True),
    sa.Column('to_address', sa.String(length=255), nullable=True),
    sa.Column('status', sa.Enum('FORWARDING', 'BOUNCING', name='statustype'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mail_bounce_status_id'), 'mail_bounce_status', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_mail_bounce_status_id'), table_name='mail_bounce_status')
    op.drop_table('mail_bounce_status')
    # ### end Alembic commands ###