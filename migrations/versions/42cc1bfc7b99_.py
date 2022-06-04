"""empty message

Revision ID: 42cc1bfc7b99
Revises: dafc30fb0795
Create Date: 2022-05-31 09:14:23.783709

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42cc1bfc7b99'
down_revision = 'dafc30fb0795'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website', sa.String(), nullable=True))
    op.add_column('artist', sa.Column('facebook_link', sa.String(length=120), nullable=True))
    op.add_column('artist', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.add_column('artist', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('artist', sa.Column('image_link', sa.String(length=500), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'image_link')
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'seeking_venue')
    op.drop_column('artist', 'facebook_link')
    op.drop_column('artist', 'website')
    # ### end Alembic commands ###