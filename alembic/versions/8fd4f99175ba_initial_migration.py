"""Initial migration

Revision ID: 8fd4f99175ba
Revises: 
Create Date: 2024-12-24 14:19:56.706489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fd4f99175ba'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('emailAddress', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('scopes', sa.String(), nullable=True),
    sa.Column('firstLogin', sa.Boolean(), nullable=True),
    sa.Column('createdBy', sa.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['createdBy'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('emailAddress')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###