
from flask import Blueprint, request, jsonify
from ..models import PDBFile

api = Blueprint('api', __name__, url_prefix='/api')

# ===== ROUTES API FILES =====

@api.route('/files', methods=['GET'])
def get_files():
    """GET /api/files - Lister tous les fichiers"""
    files = PDBFile.get_all_files()
    return jsonify({
        'status': 'success',
        'count': len(files),
        'files': [
            {
                'id': f.id,
                'filename': f.filename,
                'date': str(f.upload_date)
            }
            for f in files
        ]
    })

@api.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """GET /api/files/<id> - Récupérer un fichier par ID"""
    file = PDBFile.get_file_by_id(file_id)
    if not file:
        return jsonify({
            'status': 'error',
            'message': 'Fichier non trouvé'
        }), 404
    
    return jsonify({
        'status': 'success',
        'id': file.id,
        'filename': file.filename,
        'content_preview': file.content[:500],
        'full_content_available': len(file.content) > 500
    })

@api.route('/files', methods=['POST'])
def add_file():
    """POST /api/files - Ajouter un nouveau fichier"""
    data = request.json
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Données JSON manquantes'
        }), 400
    
    filename = data.get('filename')
    content = data.get('content')
    
    if not filename or not content:
        return jsonify({
            'status': 'error',
            'message': 'Champs requis : filename, content'
        }), 400
    
    try:
        file = PDBFile.save_pdb_file(filename, content)
        return jsonify({
            'status': 'success',
            'message': f'Fichier {filename} ajouté',
            'id': file.id
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """DELETE /api/files/<id> - Supprimer un fichier"""
    print(f"Attempting to delete file with ID: {file_id}")
    if PDBFile.delete_pdb_file(file_id):
        return jsonify({
            'status': 'success',
            'message': 'Fichier supprimé'
        })
    
    return jsonify({
        'status': 'error',
        'message': 'Fichier non trouvé'
    }), 404
