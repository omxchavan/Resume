"""Remove ResumeQA model

Revision ID: remove_resumeqa
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_resumeqa'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table('resume_qa')

def downgrade():
    op.create_table('resume_qa',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('recruiter_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['recruiter_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['resume_id'], ['resume.id'], ),
        sa.PrimaryKeyConstraint('id')
    ) 