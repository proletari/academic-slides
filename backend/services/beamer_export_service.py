"""
Beamer Export Service — renders LaTeX Beamer presentations from project data.
"""
import os
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'beamer')

# Venue → Beamer template mapping
VENUE_TEMPLATES = {
    'neurips': 'neurips.tex',
    'icml': 'neurips.tex',  # Same style
    'iclr': 'neurips.tex',
    'acl': 'neurips.tex',
    'thesis': 'thesis.tex',
    'defense': 'thesis.tex',
    'meeting': 'base.tex',
    'lecture': 'base.tex',
    'keynote': 'base.tex',
    'default': 'base.tex',
}


def get_beamer_template(venue: str) -> str:
    """Get the Beamer template filename for a given venue."""
    return VENUE_TEMPLATES.get(venue.lower(), VENUE_TEMPLATES['default'])


def render_beamer(project, venue: Optional[str] = None) -> str:
    """Render a LaTeX Beamer file from project data.

    Args:
        project: Project ORM object with pages
        venue: venue name (uses project.venue if not provided)

    Returns:
        Rendered LaTeX source code
    """
    if venue is None:
        venue = getattr(project, 'venue', None) or 'default'

    template_file = get_beamer_template(venue)

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape([]),
        block_start_string='{%',
        block_end_string='%}',
        variable_start_string='{{-',
        variable_end_string='-}}',
        comment_start_string='{#',
        comment_end_string='#}',
    )

    template = env.get_template(template_file)

    # Build slides data from project pages
    slides = []
    current_section = None

    for i, page in enumerate(project.pages):
        # Parse outline content
        outline = {}
        if page.outline_content:
            try:
                outline = json.loads(page.outline_content) if isinstance(page.outline_content, str) else page.outline_content
            except (json.JSONDecodeError, TypeError):
                outline = {}

        # Parse description content
        desc = {}
        if page.description_content:
            try:
                desc = json.loads(page.description_content) if isinstance(page.description_content, str) else page.description_content
            except (json.JSONDecodeError, TypeError):
                desc = {}

        title = outline.get('title', f'Slide {i + 1}')
        points = outline.get('points', [])

        # Get description text
        desc_text = ''
        if isinstance(desc, dict):
            desc_text = desc.get('text', '')
        elif isinstance(desc, str):
            desc_text = desc

        # Determine content type
        if points:
            content_type = 'bullets'
        elif desc_text:
            content_type = 'text'
        else:
            content_type = 'text'

        # Get speaker notes
        notes = ''
        if isinstance(desc, dict) and 'extra_fields' in desc:
            extra = desc['extra_fields']
            if isinstance(extra, dict):
                notes = extra.get('演讲者备注', extra.get('speaker_notes', ''))

        # Get section from page part
        section = getattr(page, 'part', None) or current_section
        if section != current_section:
            current_section = section
        else:
            section = None  # Only set section header once

        slide = {
            'title': _escape_latex(title),
            'section': _escape_latex(section) if section else None,
            'content_type': content_type,
            'points': [_escape_latex(p) for p in points] if points else [],
            'text': _escape_latex(desc_text) if desc_text else '',
            'notes': _escape_latex(notes) if notes else '',
        }
        slides.append(slide)

    # Build context
    title = 'Presentation'
    authors = ''
    if project.pages:
        first_outline = {}
        if project.pages[0].outline_content:
            try:
                first_outline = json.loads(project.pages[0].outline_content) if isinstance(project.pages[0].outline_content, str) else project.pages[0].outline_content
            except (json.JSONDecodeError, TypeError):
                pass
        title = first_outline.get('title', 'Presentation')

    # Try to get title/authors from idea_prompt if it looks like a paper title
    if project.idea_prompt:
        lines = project.idea_prompt.strip().split('\n')
        if len(lines) >= 1:
            title = lines[0].strip()
        if len(lines) >= 2:
            authors = lines[1].strip()

    context = {
        'title': _escape_latex(title),
        'authors': _escape_latex(authors),
        'institute': '',
        'date': project.created_at.strftime('%Y') if project.created_at else '2026',
        'show_outline': len(slides) > 3,
        'slides': slides,
    }

    return template.render(**context)


def compile_beamer(tex_source: str, output_dir: Optional[str] = None) -> Optional[str]:
    """Compile LaTeX source to PDF using pdflatex.

    Args:
        tex_source: LaTeX source code
        output_dir: directory for output (uses temp dir if None)

    Returns:
        Path to compiled PDF, or None if compilation fails
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp()

    tex_path = os.path.join(output_dir, 'presentation.tex')
    pdf_path = os.path.join(output_dir, 'presentation.pdf')

    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(tex_source)

    try:
        # Run pdflatex twice (for references/TOC)
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                logger.warning(f"pdflatex returned {result.returncode}: {result.stderr[:500]}")
                # Continue anyway — partial PDF may still be useful

        if os.path.exists(pdf_path):
            return pdf_path
        return None
    except FileNotFoundError:
        logger.warning("pdflatex not found — returning .tex only")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("pdflatex compilation timed out")
        return None


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    if not text:
        return ''
    # Order matters — backslash must be first
    text = text.replace('\\', '\\textbackslash{}')
    text = text.replace('&', '\\&')
    text = text.replace('%', '\\%')
    text = text.replace('$', '\\$')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    text = text.replace('~', '\\textasciitilde{}')
    text = text.replace('^', '\\textasciicircum{}')
    return text
