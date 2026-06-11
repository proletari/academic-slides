<div align="center">

# Academic Slides

**Generate Professional Academic Presentations from Papers, in Minutes**

A purpose-built AI tool for researchers. Upload a paper (PDF or arXiv), select your presentation venue, and get conference-ready slides with LaTeX formulas, structured sections, and a one-click Beamer export.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Node 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![CI](https://github.com/proletari/academic-slides/actions/workflows/ci-test.yml/badge.svg)](https://github.com/proletari/academic-slides/actions)

</div>

---

## Why Academic Slides?

Generic AI slide generators don't understand academic conventions. **Academic Slides** is built from the ground up for the research community:

- **Reads papers like a researcher** — extracts Introduction, Method, Experiments, Results, References from a PDF
- **Respects venue conventions** — NeurIPS oral pacing differs from a thesis defense from a group meeting
- **Renders math correctly** — KaTeX in the web preview, native LaTeX in Beamer export
- **Speaks LaTeX natively** — one-click `.tex` download, ready for `pdflatex` compilation

## Key Features

### Academic-First Pipeline

| Capability | Description |
|------------|-------------|
| **Paper Parser** | PyMuPDF-based extraction of sections, figures, tables, references from any PDF |
| **arXiv Integration** | Enter an arXiv ID; the system fetches metadata + PDF and parses it |
| **Venue-Aware Outlines** | Different structural templates for `conference` / `thesis` / `meeting` / `lecture` |
| **Academic Slide Prompts** | Per-section guidance (title / introduction / method / results / conclusion) |
| **LaTeX Formula Rendering** | `$...$` inline and `$$...$$` display math via KaTeX |
| **Beamer Export** | Jinja2-templated `.tex` output with venue-specific themes (`metropolis`, `Madrid`, `Berlin`, ...) |

### Standard Slide Workflow

| Capability | Description |
|------------|-------------|
| **Text / Outline Input** | Paste research notes or a structured outline as alternative entry points |
| **Natural Language Editing** | "Move slide 3 to ablation results" — AI handles the rewrite |
| **PPTX / PDF / Image Export** | Standard formats for any platform |
| **Multi-provider AI** | OpenAI, Anthropic, Google Gemini, or any OpenAI-compatible API |

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/proletari/academic-slides.git
cd academic-slides
cp .env.example .env
# Edit .env to add your API key
docker compose up
```

Open http://localhost:3000

### Local Development

```bash
# Backend (Python 3.10+, uses uv)
uv sync
cd backend && uv run python app.py

# Frontend (Node 18+, separate terminal)
cd frontend && npm install && npm run dev
```

## Supported Venues

| Venue | Use Case | Beamer Theme | Default Length |
|-------|----------|--------------|----------------|
| Conference | NeurIPS, ICML, ICLR, ACL oral/poster | `metropolis` | 8–15 slides |
| Thesis Defense | PhD / Master defense | `Madrid` | 15–30 slides |
| Group Meeting | Lab progress update | `default` | 5–10 slides |
| Lecture | Teaching, tutorial, workshop | `Berlin` | Topic-dependent |

## Architecture

```
academic-slides/
├── frontend/                          # React 18 + TypeScript + Vite + Zustand
│   └── src/components/academic/       # PaperUploader, ArxivInput, VenueSelector, FormulaBlock
├── backend/                           # Python Flask + SQLAlchemy
│   ├── models/
│   │   ├── paper.py                   # Paper schema (sections, figures, tables, refs)
│   │   └── academic_template.py       # Venue-specific template metadata
│   ├── services/
│   │   ├── paper_parser_service.py    # PyMuPDF + arXiv API
│   │   ├── beamer_export_service.py   # Jinja2 → .tex rendering
│   │   ├── prompts.py                 # Academic prompts (outline / slide / speaker notes)
│   │   └── ai_providers/              # Provider abstraction (OpenAI, Anthropic, Gemini, ...)
│   ├── controllers/
│   │   ├── paper_controller.py        # /api/papers, /api/papers/arxiv
│   │   └── export_controller.py       # /api/projects/{id}/export/beamer
│   └── templates/beamer/              # base.tex, neurips.tex, thesis.tex
└── docker/                            # Container orchestration
```

## Configuration

All settings are configurable via the web UI at `/settings` or through `.env`:

```env
# AI Provider
AI_PROVIDER_FORMAT=openai
API_BASE_URL=https://api.openai.com/v1
API_KEY=sk-...

# Models
TEXT_MODEL=gpt-4o
IMAGE_MODEL=gpt-image-1
```

## Roadmap

- [x] Paper PDF + arXiv ingestion with section/figure/table extraction
- [x] Venue-aware academic outline & slide prompts
- [x] LaTeX Beamer export with multiple themes
- [x] KaTeX formula rendering in web preview
- [ ] Speaker notes generation with timing suggestions
- [ ] Auto-citation insertion from parsed references
- [ ] Inline PDF compilation server-side (Tectonic)
- [ ] Multi-paper synthesis (e.g., literature review presentations)

## Acknowledgements

The core UI shell and AI orchestration layer were initially adapted from [banana-slides](https://github.com/Anionex/banana-slides) (AGPL-3.0). The academic pipeline — paper parsing, venue-aware prompts, Beamer export, LaTeX formula support, and the entire academic UX — is original work for this project.

## License

[AGPL-3.0](LICENSE) — Free and open source. Derivative works must also be released under AGPL-3.0.
