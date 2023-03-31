"""empty message

Revision ID: 938eac2ce05a
Revises: e8fb975846a0
Create Date: 2023-03-24 11:42:40.248439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '938eac2ce05a'
down_revision = 'e8fb975846a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('system_comment', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'system', ['what_system_id'], ['system_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('system_comment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###