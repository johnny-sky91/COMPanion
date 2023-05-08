"""empty message

Revision ID: ca500b5ac56c
Revises: 860e37af2e23
Create Date: 2023-04-26 11:33:22.599018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca500b5ac56c'
down_revision = '860e37af2e23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('component_soi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('main', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('usage', sa.Integer(), nullable=True))

    with op.batch_alter_table('soi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dummy', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('soi', schema=None) as batch_op:
        batch_op.drop_column('dummy')

    with op.batch_alter_table('component_soi', schema=None) as batch_op:
        batch_op.drop_column('usage')
        batch_op.drop_column('main')

    # ### end Alembic commands ###