"""empty message

Revision ID: 731c50f951d7
Revises: 
Create Date: 2023-03-15 20:11:18.911284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '731c50f951d7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('component',
    sa.Column('component_id', sa.Integer(), nullable=False),
    sa.Column('component_name', sa.String(length=160), nullable=True),
    sa.Column('component_description', sa.String(length=160), nullable=True),
    sa.Column('component_status', sa.String(length=160), nullable=True),
    sa.PrimaryKeyConstraint('component_id'),
    sa.UniqueConstraint('component_description'),
    sa.UniqueConstraint('component_name')
    )
    op.create_table('component__comment',
    sa.Column('component_comment_id', sa.Integer(), nullable=False),
    sa.Column('what_component_id', sa.Integer(), nullable=True),
    sa.Column('component_comment_text', sa.String(length=160), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('component_comment_id')
    )
    with op.batch_alter_table('component__comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_component__comment_timestamp'), ['timestamp'], unique=False)

    op.create_table('soi',
    sa.Column('soi_id', sa.Integer(), nullable=False),
    sa.Column('soi_name', sa.String(length=160), nullable=True),
    sa.Column('soi_status', sa.String(length=160), nullable=True),
    sa.PrimaryKeyConstraint('soi_id'),
    sa.UniqueConstraint('soi_name')
    )
    op.create_table('soi__comment',
    sa.Column('soi_comment_id', sa.Integer(), nullable=False),
    sa.Column('what_soi_id', sa.Integer(), nullable=True),
    sa.Column('soi_comment_text', sa.String(length=160), nullable=True),
    sa.PrimaryKeyConstraint('soi_comment_id')
    )
    op.create_table('system',
    sa.Column('system_id', sa.Integer(), nullable=False),
    sa.Column('system_name', sa.String(length=160), nullable=True),
    sa.PrimaryKeyConstraint('system_id'),
    sa.UniqueConstraint('system_name')
    )
    op.create_table('system__comment',
    sa.Column('system_comment_id', sa.Integer(), nullable=False),
    sa.Column('what_system_id', sa.Integer(), nullable=True),
    sa.Column('system_comment_text', sa.String(length=160), nullable=True),
    sa.PrimaryKeyConstraint('system_comment_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('system__comment')
    op.drop_table('system')
    op.drop_table('soi__comment')
    op.drop_table('soi')
    with op.batch_alter_table('component__comment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_component__comment_timestamp'))

    op.drop_table('component__comment')
    op.drop_table('component')
    # ### end Alembic commands ###
