"""Initial

Revision ID: a2cef0034b0e
Revises: 
Create Date: 2023-12-09 14:36:49.005595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2cef0034b0e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_premium', sa.Boolean(), nullable=False),
    sa.Column('last_request', sa.DateTime(), nullable=True),
    sa.Column('requests_per_day', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_id')
    )
    op.create_table('user_favorites_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('nm_id', sa.BigInteger(), nullable=False),
    sa.Column('period', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_account.telegram_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('wb_token_content', sa.BLOB(), nullable=True),
    sa.Column('wb_token_analytic', sa.BLOB(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user_account.telegram_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_tokens')
    op.drop_table('user_favorites_requests')
    op.drop_table('user_account')
    # ### end Alembic commands ###
