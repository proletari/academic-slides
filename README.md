<div align="center">

# Academic Slides

**From Paper to Conference Talk in Minutes**

AI-powered academic presentation generator. Upload a paper (PDF / arXiv), paste your notes, or write an outline — get professional slides with LaTeX formulas, citations, and venue-specific templates.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Node 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)

</div>

## Features

- **Paper to Slides** — Upload a PDF paper, AI extracts sections/figures/tables and generates a conference talk
- **arXiv Integration** — Enter an arXiv ID to fetch and process papers directly
- **Text to Slides** — Paste research notes, abstracts, or bullet points
- **Outline to Slides** — Provide a structured outline, AI fills in the content
- **Academic Templates** — NeurIPS, ICML, ICLR, thesis defense, group meeting, lecture
- **LaTeX Formula Support** — Inline `$...$` and display `$$...$$` math rendering with KaTeX
- **LaTeX Beamer Export** — Export `.tex` files ready to compile with `pdflatex`
- **PPTX / PDF Export** — Standard presentation formats
- **Speaker Notes** — Auto-generated talking points with timing suggestions
- **Natural Language Editing** — "Change slide 3 to ablation results" — AI handles the rest
- **Multi-provider AI** — Supports OpenAI, Anthropic Claude, Google Gemini, and more

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/YOUR_USERNAME/academic-slides.git
cd academic-slides
cp .env.example .env
# Edit .env to add your API key
docker compose up
```

Open http://localhost:3000

### Local Development

```bash
# Backend
uv sync
cd backend && uv run python app.py

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Supported Venues

| Venue | Template Type | Beamer Theme |
|-------|--------------|--------------|
| NeurIPS | Oral / Poster | `metropolis` |
| ICML | Oral / Poster | `metropolis` |
| ICLR | Oral / Poster | `metropolis` |
| ACL | Oral / Poster | `Singapore` |
| Thesis Defense | Full Presentation | `Madrid` |
| Group Meeting | Short Talk | `default` |
| Lecture | Teaching | `Berlin` |

## Architecture

```
academic-slides/
├── frontend/          # React + TypeScript + Vite
│   ├── src/
│   │   ├── pages/           # Home, OutlineEditor, DetailEditor, SlidePreview
│   │   ├── components/
│   │   │   ├── academic/    # PaperUploader, ArxivInput, VenueSelector, FormulaBlock
│   │   │   └── shared/      # Reusable UI components
│   │   ├── store/           # Zustand state management
│   │   └── api/             # Axios API layer
├── backend/           # Python Flask + SQLAlchemy
│   ├── services/
│   │   ├── ai_providers/    # OpenAI, Anthropic, Gemini, etc.
│   │   ├── paper_parser_service.py   # PDF/arXiv paper parsing
│   │   ├── beamer_export_service.py  # LaTeX Beamer generation
│   │   ├── prompts.py                # Academic AI prompts
│   │   └── export_service.py         # PPTX/PDF export
│   ├── models/              # SQLAlchemy ORM models
│   └── controllers/         # Flask API endpoints
├── templates/         # LaTeX Beamer templates
└── docker/            # Docker configuration
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

## Credits

Based on [banana-slides](https://github.com/Anionex/banana-slides) by Anionex. Licensed under AGPL-3.0.

## License

[AGPL-3.0](LICENSE) — This project is free and open source. Derivative works must also be open source under AGPL-3.0.
