"""
Paper Controller — API endpoints for paper upload, parsing, and arXiv fetch.
"""
import os
import json
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import db, Paper
from services.paper_parser_service import parse_pdf, parse_arxiv

logger = logging.getLogger(__name__)

paper_bp = Blueprint('paper', __name__, url_prefix='/api/papers')

UPLOAD_DIR = 'uploads/papers'
ALLOWED_EXTENSIONS = {'pdf'}


def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@paper_bp.route('', methods=['POST'])
def upload_paper():
    """Upload a PDF paper and parse it."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename or not _allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)

    # Parse paper
    try:
        result = parse_pdf(file_path)
    except Exception as e:
        logger.error(f"Failed to parse paper: {e}")
        return jsonify({'error': f'Failed to parse paper: {str(e)}'}), 500

    # Save to database
    paper = Paper(
        title=result.get('title', ''),
        authors=json.dumps(result.get('authors', [])),
        abstract=result.get('abstract', ''),
        file_path=file_path,
        parsed_sections=json.dumps(result.get('sections', [])),
        parsed_figures=json.dumps(result.get('figures', [])),
        parsed_tables=json.dumps(result.get('tables', [])),
        parsed_refs=json.dumps(result.get('refs', [])),
    )
    db.session.add(paper)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': paper.to_dict(),
        'parsed': result,
    }), 201


@paper_bp.route('/arxiv', methods=['POST'])
def fetch_arxiv():
    """Fetch and parse a paper from arXiv."""
    data = request.get_json()
    if not data or not data.get('arxiv_id'):
        return jsonify({'error': 'arxiv_id is required'}), 400

    arxiv_id = data['arxiv_id'].strip()
    upload_dir = os.path.join(UPLOAD_DIR, 'arxiv')
    os.makedirs(upload_dir, exist_ok=True)

    try:
        result = parse_arxiv(arxiv_id, download_dir=upload_dir)
    except Exception as e:
        logger.error(f"Failed to fetch arXiv paper {arxiv_id}: {e}")
        return jsonify({'error': f'Failed to fetch arXiv paper: {str(e)}'}), 500

    # Save to database
    paper = Paper(
        title=result.get('title', ''),
        authors=result.get('authors', '[]'),
        abstract=result.get('abstract', ''),
        arxiv_id=arxiv_id,
        file_path=result.get('file_path'),
        parsed_sections=json.dumps(result.get('sections', [])),
        parsed_figures=json.dumps(result.get('figures', [])),
        parsed_tables=json.dumps(result.get('tables', [])),
        parsed_refs=json.dumps(result.get('refs', [])),
    )
    db.session.add(paper)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': paper.to_dict(),
        'parsed': result,
    }), 201


@paper_bp.route('/<paper_id>', methods=['GET'])
def get_paper(paper_id: str):
    """Get a paper by ID."""
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': 'Paper not found'}), 404

    return jsonify({
        'success': True,
        'data': paper.to_dict(),
    })


@paper_bp.route('', methods=['GET'])
def list_papers():
    """List all papers."""
    papers = Paper.query.order_by(Paper.created_at.desc()).all()
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in papers],
    })


@paper_bp.route('/<paper_id>', methods=['DELETE'])
def delete_paper(paper_id: str):
    """Delete a paper."""
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': 'Paper not found'}), 404

    # Delete file if exists
    if paper.file_path and os.path.exists(paper.file_path):
        os.remove(paper.file_path)

    db.session.delete(paper)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Paper deleted'})
