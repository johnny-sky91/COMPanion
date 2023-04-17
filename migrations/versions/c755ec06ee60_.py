"""empty message

Revision ID: c755ec06ee60
Revises: c397c305ae13
Create Date: 2023-04-17 13:50:47.310918

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c755ec06ee60'
down_revision = 'c397c305ae13'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('component', schema=None) as batch_op:
        batch_op.add_column(sa.Column('component_check', sa.Boolean(), nullable=True))

    with op.batch_alter_table('soi', schema=None) as batch_op:
        batch_op.add_column(sa.Column('soi_check', sa.Boolean(), nullable=True))

    with op.batch_alter_table('system', schema=None) as batch_op:
        batch_op.add_column(sa.Column('system_check', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('system', schema=None) as batch_op:
        batch_op.drop_column('system_check')

    with op.batch_alter_table('soi', schema=None) as batch_op:
        batch_op.drop_column('soi_check')

    with op.batch_alter_table('component', schema=None) as batch_op:
        batch_op.drop_column('component_check')

    # ### end Alembic commands ###
