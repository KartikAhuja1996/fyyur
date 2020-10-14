"""adding seeking_description column with string data type

Revision ID: 0e63ade57863
Revises: 9ab1fc29eacc
Create Date: 2020-10-14 18:22:29.035511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e63ade57863'
down_revision = '9ab1fc29eacc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'seeking_description')
    # ### end Alembic commands ###