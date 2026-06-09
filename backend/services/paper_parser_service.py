"""
Paper Parser Service — extracts structured content from academic papers.

Uses PyMuPDF for PDF parsing with heuristic section/figure/reference extraction.
No external dependencies like GROBID required.
"""
import re
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
import httpx

logger = logging.getLogger(__name__)

# Common academic section headings (case-insensitive patterns)
SECTION_PATTERNS = [
    r'^(?:\d+\.?\s+)?(?:abstract|introduction|background)',
    r'^(?:\d+\.?\s+)?(?:related\s+work|prior\s+work)',
    r'^(?:\d+\.?\s+)?(?:method(?:ology|s)?|approach|proposed\s+method|framework)',
    r'^(?:\d+\.?\s+)?(?:experiment(?:s|al)?(?:\s+setup)?|evaluation)',
    r'^(?:\d+\.?\s+)?(?:result(?:s)?(?:\s+and\s+discussion)?)',
    r'^(?:\d+\.?\s+)?(?:discussion|analysis)',
    r'^(?:\d+\.?\s+)?(?:conclusion(?:s)?|summary|closing)',
    r'^(?:\d+\.?\s+)?(?:acknowledgment(?:s)?|acknowledgement(?:s)?)',
    r'^(?:\d+\.?\s+)?(?:reference(?:s)?|bibliography)',
    r'^(?:\d+\.?\s+)?(?:appendix|supplementary)',
]

SECTION_RE = re.compile('|'.join(SECTION_PATTERNS), re.IGNORECASE)

# Figure caption pattern
FIGURE_RE = re.compile(
    r'(?:fig(?:ure)?\.?\s*\d+[.:]\s*)(.+?)(?:\n|$)',
    re.IGNORECASE
)

# Table caption pattern
TABLE_RE = re.compile(
    r'(?:table\s*\d+[.:]\s*)(.+?)(?:\n|$)',
    re.IGNORECASE
)

# Reference pattern: [1] Author, Title, ...
REF_RE = re.compile(
    r'^\[(\d+)\]\s+(.+?)(?:\n|$)',
    re.MULTILINE
)


def parse_pdf(file_path: str) -> dict:
    """Parse a PDF paper and extract structured content.

    Returns:
        dict with keys: title, authors, abstract, sections, figures, tables, refs
    """
    doc = fitz.open(file_path)
    try:
        full_text = ""
        page_texts = []
        for page in doc:
            page_texts.append(page.get_text())
        full_text = "\n\n".join(page_texts)

        title = _extract_title(doc, full_text)
        authors = _extract_authors(doc, full_text)
        abstract = _extract_abstract(full_text)
        sections = _extract_sections(full_text)
        figures = _extract_figures(doc)
        tables = _extract_tables(full_text)
        refs = _extract_references(full_text)

        return {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'sections': sections,
            'figures': figures,
            'tables': tables,
            'refs': refs,
        }
    finally:
        doc.close()


def parse_arxiv(arxiv_id: str, download_dir: Optional[str] = None) -> dict:
    """Fetch a paper from arXiv and parse it.

    Args:
        arxiv_id: arXiv paper ID (e.g. "2301.07041")
        download_dir: directory to save the PDF (uses temp dir if None)

    Returns:
        Same dict as parse_pdf, plus arxiv_id field
    """
    # Fetch metadata from arXiv API
    metadata = _fetch_arxiv_metadata(arxiv_id)

    # Download PDF
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    if download_dir is None:
        download_dir = tempfile.mkdtemp()
    pdf_path = Path(download_dir) / f"{arxiv_id.replace('/', '_')}.pdf"

    logger.info(f"Downloading arXiv paper {arxiv_id} from {pdf_url}")
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        resp = client.get(pdf_url)
        resp.raise_for_status()
        pdf_path.write_bytes(resp.content)

    # Parse the downloaded PDF
    result = parse_pdf(str(pdf_path))
    result['arxiv_id'] = arxiv_id

    # Override with arXiv metadata if available
    if metadata.get('title'):
        result['title'] = metadata['title']
    if metadata.get('authors'):
        result['authors'] = json.dumps(metadata['authors'])
    if metadata.get('abstract'):
        result['abstract'] = metadata['abstract']

    return result


def _fetch_arxiv_metadata(arxiv_id: str) -> dict:
    """Fetch paper metadata from arXiv API."""
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(url)
            resp.raise_for_status()
            text = resp.text

        # Simple XML parsing for title, authors, summary
        title_match = re.search(r'<title>(.+?)</title>', text, re.DOTALL)
        summary_match = re.search(r'<summary>(.+?)</summary>', text, re.DOTALL)
        author_matches = re.findall(r'<name>(.+?)</name>', text)

        # The first <title> is the feed title, skip it
        titles = re.findall(r'<title>(.+?)</title>', text, re.DOTALL)
        title = titles[1].strip() if len(titles) > 1 else None

        return {
            'title': title,
            'authors': author_matches if author_matches else None,
            'abstract': summary_match.group(1).strip() if summary_match else None,
        }
    except Exception as e:
        logger.warning(f"Failed to fetch arXiv metadata for {arxiv_id}: {e}")
        return {}


def _extract_title(doc, text: str) -> str:
    """Extract paper title — heuristic: largest font on first page, or first non-empty line."""
    try:
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]
        # Find the block with the largest font size on the first page
        max_size = 0
        title = ""
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if span["size"] > max_size and len(span["text"].strip()) > 3:
                        max_size = span["size"]
                        title = span["text"].strip()
        if title:
            return title
    except Exception:
        pass

    # Fallback: first non-empty line
    for line in text.split('\n'):
        line = line.strip()
        if len(line) > 5 and not line.lower().startswith(('abstract', 'introduction')):
            return line
    return "Untitled Paper"


def _extract_authors(doc, text: str) -> str:
    """Extract author names — heuristic: lines between title and abstract."""
    lines = text.split('\n')
    title_found = False
    abstract_found = False
    author_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not title_found:
            title_found = True
            continue
        if SECTION_RE.match(stripped.lower()) and 'abstract' in stripped.lower():
            abstract_found = True
            break
        # Author lines typically contain commas, university affiliations, or @
        if any(kw in stripped.lower() for kw in ['university', 'institute', '@', 'lab', 'college', ',']):
            author_lines.append(stripped)
        elif len(stripped) < 100 and not stripped[0].isdigit():
            author_lines.append(stripped)

    if author_lines:
        return json.dumps(author_lines[:10])  # Limit to 10 lines
    return json.dumps([])


def _extract_abstract(text: str) -> str:
    """Extract the abstract section."""
    # Look for "Abstract" heading
    abstract_match = re.search(
        r'(?:^|\n)\s*(?:\d+\.?\s*)?abstract\s*[:\-—]?\s*\n(.+?)(?:\n\s*(?:\d+\.?\s*)?(?:introduction|keywords|1\s*\.))',
        text, re.IGNORECASE | re.DOTALL
    )
    if abstract_match:
        return abstract_match.group(1).strip()

    # Fallback: look for text between "Abstract" and next section
    lines = text.split('\n')
    in_abstract = False
    abstract_lines = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'^(?:\d+\.?\s*)?abstract', stripped, re.IGNORECASE):
            in_abstract = True
            # Check if abstract text is on the same line
            rest = re.sub(r'^(?:\d+\.?\s*)?abstract\s*[:\-—]?\s*', '', stripped, flags=re.IGNORECASE)
            if rest:
                abstract_lines.append(rest)
            continue
        if in_abstract:
            if SECTION_RE.match(stripped.lower()) and 'abstract' not in stripped.lower():
                break
            abstract_lines.append(stripped)

    return ' '.join(abstract_lines).strip() if abstract_lines else ""


def _extract_sections(text: str) -> list:
    """Extract sections with their content."""
    lines = text.split('\n')
    sections = []
    current_section = None
    current_content = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_content:
                current_content.append('')
            continue

        # Check if this line is a section heading
        if SECTION_RE.match(stripped.lower()) and len(stripped) < 100:
            # Save previous section
            if current_section:
                sections.append({
                    'title': current_section,
                    'level': 1,
                    'content': '\n'.join(current_content).strip(),
                })
            current_section = stripped
            current_content = []
        elif current_section:
            current_content.append(stripped)

    # Save last section
    if current_section:
        sections.append({
            'title': current_section,
            'level': 1,
            'content': '\n'.join(current_content).strip(),
        })

    return sections


def _extract_figures(doc) -> list:
    """Extract figures with their captions from the PDF."""
    figures = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        for match in FIGURE_RE.finditer(text):
            figures.append({
                'caption': match.group(1).strip(),
                'page_num': page_num + 1,
                'path': None,  # Could be extended to extract actual images
            })
    return figures


def _extract_tables(text: str) -> list:
    """Extract table captions from the text."""
    tables = []
    for match in TABLE_RE.finditer(text):
        tables.append({
            'caption': match.group(1).strip(),
            'data': None,  # Could be extended with table extraction
        })
    return tables


def _extract_references(text: str) -> list:
    """Extract reference list from the paper."""
    refs = []
    # Find the references section
    ref_section_match = re.search(
        r'(?:^|\n)\s*(?:\d+\.?\s*)?(?:references|bibliography)\s*\n(.+)',
        text, re.IGNORECASE | re.DOTALL
    )
    if not ref_section_match:
        return refs

    ref_text = ref_section_match.group(1)

    for match in REF_RE.finditer(ref_text):
        ref_num = match.group(1)
        ref_content = match.group(2).strip()

        # Try to parse author, title from the reference
        parts = ref_content.split('.', 2)
        authors = parts[0].strip() if len(parts) > 0 else ""
        title = parts[1].strip() if len(parts) > 1 else ref_content

        refs.append({
            'key': ref_num,
            'authors': authors,
            'title': title,
            'raw': ref_content,
        })

    return refs
