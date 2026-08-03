from flask import Blueprint, request, jsonify
from ..models import TempSaveScoreOneFile

api = Blueprint('api', __name__, url_prefix='/api') # add score to the url prefix

# ===== ROUTES API =====

@api.route('/getDataWhithUserKey/<string:userKey>', methods=['GET'])
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

@api.route('/generateUserKey', methods=['GET'])
def generate_user_key():
    """Génère un user_key unique"""
    user_key = TempSaveScoreOneFile.generate_user_key()
    return jsonify({
        'status': 'success',
        'user_key': user_key
    })

@api.route('/saveDataWithUserKey/<string:userKey>', methods=['POST'])
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
