import random
import string

from flask import Blueprint, request, jsonify
from ..models import TempSaveScoreOneFile
from ..models import TempSaveComparison

apiScore = Blueprint('api-database-score', __name__, url_prefix='/api-database-score')
apiComparison = Blueprint('api-database-comparison', __name__, url_prefix='/api-database-comparison')

apiKey = Blueprint('api-key', __name__, url_prefix='/api-key')
# ===== ROUTES API =====

@apiScore.route('/getDataWhithUserKey/<string:userKey>', methods=['GET'])
def get_data_with_user_key(userKey):
    """Récupère les données de score par user_key"""
    score_data = TempSaveScoreOneFile.get_by_user_key(userKey)
    if not score_data:
        return jsonify({
            'status': 'error',
            'message': 'Aucune donnée trouvée pour ce user_key'
        })
    
    return jsonify({
        'status': 'success',
        'user_key': score_data.user_key,
        'parameter': score_data.parameter,
        'cif_file_name': score_data.cif_file_name,
        'cif_file_content': score_data.cif_file_content,
        'csv_file_name': score_data.csv_file_name,
        'csv_file_content': score_data.csv_file_content,
        'log_file_name': score_data.log_file_name,
        'log_file_content': score_data.log_file_content
    })

@apiScore.route('/saveDataWithUserKey/<string:userKey>', methods=['POST'])
def save_data_with_user_key(userKey):
    """Sauvegarde les données de score dans la BD par user_key"""
    data = request.json
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Données JSON manquantes'
        }), 400
    
    parameter = data.get('parameter')
    cif_file_name = data.get('cif_file_name')
    cif_file_content = data.get('cif_file_content')
    csv_file_name = data.get('csv_file_name')
    csv_file_content = data.get('csv_file_content')
    log_file_name = data.get('log_file_name')
    log_file_content = data.get('log_file_content')
    
    if not all([parameter, cif_file_name, cif_file_content, csv_file_name, csv_file_content]):
        return jsonify({
            'status': 'error',
            'message': 'Champs requis : parameter, cif_file_name, cif_file_content, csv_file_name, csv_file_content'
        }), 400
    
    try:
        TempSaveScoreOneFile.save_score_data(userKey, parameter, cif_file_name, cif_file_content, csv_file_name, csv_file_content, log_file_name, log_file_content)
        return jsonify({
            'status': 'success',
            'message': f'Données sauvegardées pour le user_key {userKey}'
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@apiKey.route('/generateUserKey', methods=['GET'])
def generate_user_key():
    """Génère un user_key unique"""

    user_key = None

    is_unique = False
    while not is_unique:

        is_unique = True
        user_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        if TempSaveScoreOneFile.user_key_exists(user_key):
            is_unique = False

        if TempSaveComparison.user_key_exists(user_key):
            is_unique = False
        
    return jsonify({
        'status': 'success',
        'user_key': user_key
    })

@apiComparison.route('/getDataWhithUserKey/<string:userKey>', methods=['GET'])
def get_data_with_user_key(userKey):
    """Récupère les données de score par user_key"""
    comparison_data = TempSaveComparison.get_by_user_key(userKey)
    if not comparison_data:
        return jsonify({
            'status': 'error',
            'message': 'Aucune donnée trouvée pour ce user_key'
        })
    
    return jsonify({
        'status': 'success',
        'user_key': comparison_data.user_key,
        'data': comparison_data.data,
        'parameter': comparison_data.parameter
    })

@apiComparison.route('/saveDataWithUserKey/<string:userKey>', methods=['POST'])
def save_data_with_user_key(userKey):
    """Sauvegarde les données de score dans la BD par user_key"""
    data_request = request.json
    if not data_request:
        return jsonify({
            'status': 'error',
            'message': 'Données JSON manquantes'
        }), 400
    
    data = data_request.get('data')
    parameter = data_request.get('parameter')
    
    if not all([data, parameter]):
        return jsonify({
            'status': 'error',
            'message': 'Champs requis : data and parameter'
        }), 400
    
    try:
        TempSaveComparison.save_comparison_data(userKey, data, parameter)
        return jsonify({
            'status': 'success',
            'message': f'Données sauvegardées pour le user_key {userKey}'
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500