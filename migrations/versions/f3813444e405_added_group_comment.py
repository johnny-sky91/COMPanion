"""added group_comment

Revision ID: f3813444e405
Revises: 56d98d6ae7b6
Create Date: 2023-09-18 10:24:01.319820

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3813444e405'
down_revision = '56d98d6ae7b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group_comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(length=160), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('group_comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_group_comment_timestamp'), ['timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_comment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_group_comment_timestamp'))

    op.drop_table('group_comment')
    # ### end Alembic commands ###
