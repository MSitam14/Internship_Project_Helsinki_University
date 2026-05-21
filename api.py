"""
API routes pour les fichiers PDB.
Fonctions utilitaires et endpoints API.
"""

from flask import Blueprint, request, jsonify
from database import db, PDBFile

api = Blueprint('api', __name__, url_prefix='/api')

# # ===== FONCTIONS UTILITAIRES =====

# def get_all_files():
#     """Récupère tous les fichiers PDB"""
#     return PDBFile.query.all()

# def get_file_by_id(file_id):
#     """Récupère un fichier par son ID"""
#     return PDBFile.query.get(file_id)

# def get_file_by_name(filename):
#     """Récupère un fichier par son nom"""
#     return PDBFile.query.filter_by(filename=filename).first()

# def save_pdb_file(filename, content):
#     """Sauvegarde un nouveau fichier PDB dans la BD"""
#     pdb_file = PDBFile(filename=filename, content=content)
#     db.session.add(pdb_file)
#     db.session.commit()
#     return pdb_file

# def delete_pdb_file(file_id):
#     """Supprime un fichier PDB de la BD"""
#     pdb_file = PDBFile.query.get(file_id)
#     if pdb_file:
#         db.session.delete(pdb_file)
#         db.session.commit()
#         return True
#     return False

# ===== ROUTES API =====

@api.route('/files', methods=['GET'])
def get_files():
    """GET /api/files - Lister tous les fichiers"""
    files = get_all_files()
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
    file = get_file_by_id(file_id)
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
        file = save_pdb_file(filename, content)
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
    if delete_pdb_file(file_id):
        return jsonify({
            'status': 'success',
            'message': 'Fichier supprimé'
        })
    
    return jsonify({
        'status': 'error',
        'message': 'Fichier non trouvé'
    }), 404
