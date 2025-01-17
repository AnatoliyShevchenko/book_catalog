"""fix

Revision ID: 05170027085e
Revises: a65f68d33496
Create Date: 2024-07-23 15:45:26.069786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05170027085e'
down_revision: Union[str, None] = 'a65f68d33496'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('genre_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(None, 'books', 'genres', ['genre_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'books', type_='foreignkey')
    op.drop_column('books', 'genre_id')
    # ### end Alembic commands ###
