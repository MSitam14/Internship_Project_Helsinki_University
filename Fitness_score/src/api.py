from flask import Blueprint, request, jsonify

api = Blueprint('api-score', __name__, url_prefix='/api-score')

@api.route('/test', methods=['GET'])
def get_files():
    """GET /api-score/test - test api"""
    return jsonify({
        'status': 'success',
        'message': 'api-score is working!'
    })