"""empty message

Revision ID: 76282eb453c7
Revises: b8cb46e27e81
Create Date: 2023-03-21 15:12:29.810040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "76282eb453c7"
down_revision = "b8cb46e27e81"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("soi__comment", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("timestamp_soi_comment", sa.DateTime(), nullable=True)
        )
        batch_op.create_index(
            batch_op.f("ix_soi__comment_timestamp_soi_comment"),
            ["timestamp_soi_comment"],
            unique=False,
        )
        batch_op.create_foreign_key(None, "soi", ["what_soi_id"], ["soi_id"])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("soi__comment", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_soi__comment_timestamp_soi_comment"))
        batch_op.drop_column("timestamp_soi_comment")

    # ### end Alembic commands ###
