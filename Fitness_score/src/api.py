import json
import os
import base64
from .Scoring_website import score
from .tools import translate_path


from flask import Blueprint, request, jsonify

api = Blueprint('api-score', __name__, url_prefix='/api-score')


def _json_safe(value):
    """Convert non-JSON values (notably bytes) into JSON-serializable values."""
    if isinstance(value, bytes):
        return {
            'encoding': 'base64',
            'data': base64.b64encode(value).decode('ascii')
        }
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value

@api.route('/test', methods=['GET'])
def get_files():
    """GET /api-score/test - test api"""
    return jsonify({
        'status': 'success',
        'message': 'api-score is working!'
    })

@api.route('/score', methods=['POST'])
def calculate_score():    
    """POST /api-score/score - calculate fitness score"""
    data = request.get_json()
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No input data provided'
        }), 400

    try:
        params = data['params']
        pdb = data['pdb']
    except KeyError as e:
        return jsonify({
            'status': 'error',
            'message': f'Missing parameter: {str(e)}'
        }), 400

    params = data['params']
    pdb = data['pdb']
    pdb_path = '../data/input/structures/'+pdb["pdb_name"]

    with open(translate_path(pdb_path), 'w') as f:
        f.write(pdb["pdb_content"])
    
    try:
        out = score(params, pdb_path) 
    except Exception as e:
        os.remove(translate_path(pdb_path))
        return jsonify({
            'status': 'error',
            'message': f'Error during scoring: {str(e)}'
        }), 500

    try: os.remove(translate_path(pdb_path))
    except OSError: print(f"File '{pdb_path}' not found.")

    return jsonify({
        'status': 'success',
        'content': _json_safe(out)
    })