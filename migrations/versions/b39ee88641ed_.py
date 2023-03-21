"""empty message

Revision ID: b39ee88641ed
Revises: 76282eb453c7
Create Date: 2023-03-21 15:16:18.856429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b39ee88641ed'
down_revision = '76282eb453c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('system_comment',
    sa.Column('system_comment_id', sa.Integer(), nullable=False),
    sa.Column('what_system_id', sa.Integer(), nullable=True),
    sa.Column('system_comment_text', sa.String(length=160), nullable=True),
    sa.PrimaryKeyConstraint('system_comment_id')
    )
    op.create_table('component_comment',
    sa.Column('component_comment_id', sa.Integer(), nullable=False),
    sa.Column('what_component_id', sa.Integer(), nullable=True),
    sa.Column('component_comment_text', sa.String(length=160), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['what_component_id'], ['component.component_id'], ),
    sa.PrimaryKeyConstraint('component_comment_id')
    )
    with op.batch_alter_table('component_comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_component_comment_timestamp'), ['timestamp'], unique=False)

    op.create_table('soi_comment',
    sa.Column('soi_comment_id', sa.Integer(), nullable=False),
    sa.Column('what_soi_id', sa.Integer(), nullable=True),
    sa.Column('soi_comment_text', sa.String(length=160), nullable=True),
    sa.Column('timestamp_soi_comment', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['what_soi_id'], ['soi.soi_id'], ),
    sa.PrimaryKeyConstraint('soi_comment_id')
    )
    with op.batch_alter_table('soi_comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_soi_comment_timestamp_soi_comment'), ['timestamp_soi_comment'], unique=False)

    with op.batch_alter_table('component__comment', schema=None) as batch_op:
        batch_op.drop_index('ix_component__comment_timestamp')

    op.drop_table('component__comment')
    op.drop_table('system__comment')
    op.drop_table('soi__comment')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('soi__comment',
    sa.Column('soi_comment_id', sa.INTEGER(), nullable=False),
    sa.Column('what_soi_id', sa.INTEGER(), nullable=True),
    sa.Column('soi_comment_text', sa.VARCHAR(length=160), nullable=True),
    sa.PrimaryKeyConstraint('soi_comment_id')
    )
    op.create_table('system__comment',
    sa.Column('system_comment_id', sa.INTEGER(), nullable=False),
    sa.Column('what_system_id', sa.INTEGER(), nullable=True),
    sa.Column('system_comment_text', sa.VARCHAR(length=160), nullable=True),
    sa.PrimaryKeyConstraint('system_comment_id')
    )
    op.create_table('component__comment',
    sa.Column('component_comment_id', sa.INTEGER(), nullable=False),
    sa.Column('what_component_id', sa.INTEGER(), nullable=True),
    sa.Column('component_comment_text', sa.VARCHAR(length=160), nullable=True),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['what_component_id'], ['component.component_id'], ),
    sa.PrimaryKeyConstraint('component_comment_id')
    )
    with op.batch_alter_table('component__comment', schema=None) as batch_op:
        batch_op.create_index('ix_component__comment_timestamp', ['timestamp'], unique=False)

    with op.batch_alter_table('soi_comment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_soi_comment_timestamp_soi_comment'))

    op.drop_table('soi_comment')
    with op.batch_alter_table('component_comment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_component_comment_timestamp'))

    op.drop_table('component_comment')
    op.drop_table('system_comment')
    # ### end Alembic commands ###