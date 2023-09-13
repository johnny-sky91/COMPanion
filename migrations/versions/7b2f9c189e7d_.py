"""empty message

Revision ID: 7b2f9c189e7d
Revises: a7afc2226989
Create Date: 2023-09-12 11:40:31.666850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b2f9c189e7d'
down_revision = 'a7afc2226989'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('soi_id')
        batch_op.drop_column('component_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('component_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('soi_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key(None, 'soi', ['soi_id'], ['id'])
        batch_op.create_foreign_key(None, 'component', ['component_id'], ['id'])

    # ### end Alembic commands ###