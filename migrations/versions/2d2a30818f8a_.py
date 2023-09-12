"""empty message

Revision ID: 2d2a30818f8a
Revises: f952848c8b03
Create Date: 2023-09-12 10:08:36.866671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d2a30818f8a'
down_revision = 'f952848c8b03'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=160), nullable=False))
        batch_op.drop_column('text')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('text', sa.VARCHAR(length=160), nullable=False))
        batch_op.drop_column('name')

    # ### end Alembic commands ###
