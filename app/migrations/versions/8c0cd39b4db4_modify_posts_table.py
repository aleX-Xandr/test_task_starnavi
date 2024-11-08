"""Modify posts table

Revision ID: 8c0cd39b4db4
Revises: 020c0892332d
Create Date: 2024-11-08 03:18:20.093893

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c0cd39b4db4'
down_revision: Union[str, None] = '020c0892332d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('auto_comment_timeout', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'auto_comment_timeout')
    # ### end Alembic commands ###
