"""Added check & status for Group

Revision ID: 3b41a940bdf2
Revises: 2aca586ca15f
Create Date: 2023-09-13 14:20:43.991433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b41a940bdf2'
down_revision = '2aca586ca15f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column('check', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.drop_column('check')
        batch_op.drop_column('status')

    # ### end Alembic commands ###
