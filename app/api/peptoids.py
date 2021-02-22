from app.api import bp
from flask import jsonify, url_for
from app.models import Peptoid, Author, Residue
from app import limiter


@bp.route('/peptoids/<code>', methods=['GET'])
@limiter.limit("1000 per minute")
def get_peptoid(code):
    return jsonify(Peptoid.query.get_or_404(code).to_dict())


@bp.route('/peptoids', methods=['GET'])
@limiter.limit("1000 per minute")
def get_peptoids():
    data = []
    for p in Peptoid.query.all():
        data.append({p.code:p.to_dict()})
    return jsonify(data)

@bp.route('/residues', methods=['GET'])
@limiter.limit("1000 per minute")
def get_residues():
    data = []
    for r in Residue.query.all():
        data.append({r.long_name:r.to_dict()})
    return jsonify(data)

@bp.route('/authors', methods=['GET'])
@limiter.limit("1000 per minute")
def get_authors():
    data = []
    for a in Author.query.all():
        data.append({a.last_name:a.to_dict()})
    return jsonify(data)


@bp.route('/peptoids/<code>/residues', methods=['GET'])
@limiter.limit("1000 per minute")
def get_pep_residues(code):
    data = {}
    i = 1
    for r in Peptoid.query.get_or_404(code).peptoid_residue:
        data[f'Residue {i}'] = r.to_dict()
        i += 1
    return jsonify(data)


@bp.route('/peptoids/<code>/authors', methods=['GET'])
@limiter.limit("1000 per minute")
def get_pep_authors(code):
    data = {}
    i = 1
    for a in Peptoid.query.get_or_404(code).peptoid_author:
        data[f'Author {i}'] = a.to_dict()
        i += 1
    return jsonify(data)
