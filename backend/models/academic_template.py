"""
AcademicTemplate model — venue-specific presentation templates.
"""
import uuid
from datetime import datetime
from . import db


class AcademicTemplate(db.Model):
    """Academic presentation template tied to a specific venue/type."""
    __tablename__ = 'academic_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)       # "NeurIPS Oral"
    venue = db.Column(db.String(50), nullable=False)       # "neurips", "icml", "thesis"
    type = db.Column(db.String(20), nullable=False)        # "poster", "oral", "lecture"
    beamer_theme = db.Column(db.String(50), nullable=True) # LaTeX Beamer theme name
    slide_structure = db.Column(db.Text, nullable=True)    # JSON: default slide structure
    css_styles = db.Column(db.Text, nullable=True)         # web preview CSS overrides
    thumbnail = db.Column(db.String(500), nullable=True)   # thumbnail image path
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'template_id': self.id,
            'name': self.name,
            'venue': self.venue,
            'type': self.type,
            'beamer_theme': self.beamer_theme,
            'thumbnail': self.thumbnail,
        }

    def __repr__(self):
        return f'<AcademicTemplate {self.name} ({self.venue})>'
