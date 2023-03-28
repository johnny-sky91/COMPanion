"""empty message

Revision ID: ef036584878e
Revises: 5f0e243a91ff
Create Date: 2023-03-24 14:36:36.845882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef036584878e'
down_revision = '5f0e243a91ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('system_comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('system_comment_id', sa.Integer(), nullable=False))
        batch_op.drop_column('comment_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('system_comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment_id', sa.INTEGER(), nullable=False))
        batch_op.drop_column('system_comment_id')

    # ### end Alembic commands ###
