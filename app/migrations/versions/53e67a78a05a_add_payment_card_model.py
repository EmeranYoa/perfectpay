"""add payment card model

Revision ID: 53e67a78a05a
Revises: b3eada959c96
Create Date: 2025-02-23 10:56:49.324796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53e67a78a05a'
down_revision: Union[str, None] = 'b3eada959c96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_cards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('last_four_digits', sa.String(length=255), nullable=False),
    sa.Column('card_type', sa.String(length=20), nullable=False),
    sa.Column('expiration_month', sa.Integer(), nullable=False),
    sa.Column('expiration_year', sa.Integer(), nullable=False),
    sa.Column('tms_token', sa.String(length=255), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_cards_id'), 'payment_cards', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payment_cards_id'), table_name='payment_cards')
    op.drop_table('payment_cards')
    # ### end Alembic commands ###
