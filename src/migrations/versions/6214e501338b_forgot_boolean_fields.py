"""forgot boolean fields

Revision ID: 6214e501338b
Revises: e2218152bce0
Create Date: 2024-07-22 14:32:50.450782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6214e501338b'
down_revision: Union[str, None] = 'e2218152bce0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reserv', sa.Column('on_hands', sa.Boolean(), nullable=False))
    op.add_column('reserv', sa.Column('is_returned', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reserv', 'is_returned')
    op.drop_column('reserv', 'on_hands')
    # ### end Alembic commands ###