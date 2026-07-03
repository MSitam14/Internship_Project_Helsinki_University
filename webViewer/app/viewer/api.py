from flask import Blueprint, request, jsonify
from ..models import TempSaveScoreOneFile

api = Blueprint('api', __name__, url_prefix='/api')

# ===== ROUTES API =====

@api.route('/getDataWhithUserKey/<string:userKey>', methods=['GET'])
def get_data_with_user_key(userKey):
    """Récupère les données de score par user_key"""
    score_data = TempSaveScoreOneFile.get_by_user_key(userKey)
    if not score_data:
        return jsonify({
            'status': 'error',
            'message': 'Aucune donnée trouvée pour ce user_key'
        }), 204
    
    return jsonify({
        'status': 'success',
        'user_key': score_data.user_key,
        'parameter': score_data.parameter,
        'cif_file_name': score_data.cif_file_name,
        'cif_file_content': score_data.cif_file_content,
        'csv_file_name': score_data.csv_file_name,
        'csv_file_content': score_data.csv_file_content
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
    
    if not all([parameter, cif_file_name, cif_file_content, csv_file_name, csv_file_content]):
        return jsonify({
            'status': 'error',
            'message': 'Champs requis : parameter, cif_file_name, cif_file_content, csv_file_name, csv_file_content'
        }), 400
    
    try:
        TempSaveScoreOneFile.save_score_data(userKey, parameter, cif_file_name, cif_file_content, csv_file_name, csv_file_content)
        return jsonify({
            'status': 'success',
            'message': f'Données sauvegardées pour le user_key {userKey}'
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500




# ===== ROUTES API FILES =====

# @api.route('/files', methods=['GET'])
# def get_files():
#     """GET /api/files - Lister tous les fichiers"""
#     files = PDBFile.get_all_files()
#     return jsonify({
#         'status': 'success',
#         'count': len(files),
#         'files': [
#             {
#                 'id': f.id,
#                 'filename': f.filename,
#             }
#             for f in files
#         ]
#     })

# @api.route('/files/<int:file_id>', methods=['GET'])
# def get_file(file_id):
#     """GET /api/files/<id> - Récupérer un fichier par ID"""
#     file = PDBFile.get_file_by_id(file_id)
#     if not file:
#         return jsonify({
#             'status': 'error',
#             'message': 'Fichier non trouvé'
#         }), 404
    
#     return jsonify({
#         'status': 'success',
#         'id': file.id,
#         'filename': file.filename,
#         'content_preview': file.content[:500],
#         'full_content_available': len(file.content) > 500
#     })

# @api.route('/files', methods=['POST'])
# def add_file():
#     """POST /api/files - Ajouter un nouveau fichier"""
#     data = request.json
    
#     if not data:
#         return jsonify({
#             'status': 'error',
#             'message': 'Données JSON manquantes'
#         }), 400
    
#     filename = data.get('filename')
#     content = data.get('content')
    
#     if not filename or not content:
#         return jsonify({
#             'status': 'error',
#             'message': 'Champs requis : filename, content'
#         }), 400
    
#     try:
#         file = PDBFile.save_pdb_file(filename, content)
#         return jsonify({
#             'status': 'success',
#             'message': f'Fichier {filename} ajouté',
#             'id': file.id
#         }), 201
#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500

# @api.route('/files/<int:file_id>', methods=['DELETE'])
# def delete_file(file_id):
#     """DELETE /api/files/<id> - Supprimer un fichier"""
#     print(f"Attempting to delete file with ID: {file_id}")
#     if PDBFile.delete_pdb_file(file_id):
#         return jsonify({
#             'status': 'success',
#             'message': 'Fichier supprimé'
#         })
    
#     return jsonify({
#         'status': 'error',
#         'message': 'Fichier non trouvé'
#     }), 404
