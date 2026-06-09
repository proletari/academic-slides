"""
Paper model — stores uploaded academic papers and their parsed content.
"""
import uuid
from datetime import datetime
from . import db


class Paper(db.Model):
    """Represents an uploaded academic paper (PDF or arXiv)."""
    __tablename__ = 'papers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(500), nullable=True)
    authors = db.Column(db.Text, nullable=True)          # JSON list of author names
    abstract = db.Column(db.Text, nullable=True)
    arxiv_id = db.Column(db.String(50), nullable=True)    # e.g. "2301.07041"
    file_path = db.Column(db.String(500), nullable=True)  # stored PDF path
    parsed_sections = db.Column(db.Text, nullable=True)   # JSON: [{title, level, content}]
    parsed_figures = db.Column(db.Text, nullable=True)    # JSON: [{path, caption, page_num}]
    parsed_tables = db.Column(db.Text, nullable=True)     # JSON: [{data, caption, page_num}]
    parsed_refs = db.Column(db.Text, nullable=True)       # JSON: [{key, title, authors, year}]
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'paper_id': self.id,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'arxiv_id': self.arxiv_id,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }

    def __repr__(self):
        return f'<Paper {self.id}: {self.title}>'
