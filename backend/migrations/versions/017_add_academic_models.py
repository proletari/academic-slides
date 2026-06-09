"""add academic models (papers, academic_templates, project academic fields)

Revision ID: 017
Revises: c153f8c4e111
Create Date: 2026-06-09 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '017'
down_revision = 'c153f8c4e111'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create papers table
    op.create_table(
        'papers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('authors', sa.Text, nullable=True),
        sa.Column('abstract', sa.Text, nullable=True),
        sa.Column('arxiv_id', sa.String(length=50), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('parsed_sections', sa.Text, nullable=True),
        sa.Column('parsed_figures', sa.Text, nullable=True),
        sa.Column('parsed_tables', sa.Text, nullable=True),
        sa.Column('parsed_refs', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create academic_templates table
    op.create_table(
        'academic_templates',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('venue', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('beamer_theme', sa.String(length=50), nullable=True),
        sa.Column('slide_structure', sa.Text, nullable=True),
        sa.Column('css_styles', sa.Text, nullable=True),
        sa.Column('thumbnail', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Add academic fields to projects table
    op.add_column('projects', sa.Column('paper_id', sa.String(length=36), nullable=True))
    op.add_column('projects', sa.Column('venue', sa.String(length=50), nullable=True))
    op.add_column('projects', sa.Column('academic_template_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('fk_projects_paper_id', 'projects', 'papers', ['paper_id'], ['id'])
    op.create_foreign_key('fk_projects_academic_template_id', 'projects', 'academic_templates', ['academic_template_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_projects_academic_template_id', 'projects', type_='foreignkey')
    op.drop_constraint('fk_projects_paper_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'academic_template_id')
    op.drop_column('projects', 'venue')
    op.drop_column('projects', 'paper_id')
    op.drop_table('academic_templates')
    op.drop_table('papers')
