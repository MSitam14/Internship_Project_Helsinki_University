"""
Configuration et modèles de la base de données.
"""

from . import db

class PDBFile(db.Model):
    """Modèle pour les fichiers PDB"""
    __tablename__ = 'pdb_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<PDBFile {self.filename}>'

    @staticmethod
    def get_all_files():
        """Récupère tous les fichiers PDB"""
        return PDBFile.query.all()
    
    @staticmethod
    def get_file_by_id(file_id):
        """Récupère un fichier par son ID"""
        return PDBFile.query.get(file_id)

    @staticmethod
    def get_file_by_name(filename):
        """Récupère un fichier par son nom"""
        return PDBFile.query.filter_by(filename=filename).first()

    @staticmethod
    def save_pdb_file(filename, content):
        """Sauvegarde un nouveau fichier PDB dans la BD"""
        pdb_file = PDBFile(filename=filename, content=content)
        db.session.add(pdb_file)
        db.session.commit()
        return pdb_file

    @staticmethod
    def delete_pdb_file(file_id):
        """Supprime un fichier PDB de la BD"""
        pdb_file = PDBFile.query.get(file_id)
        if pdb_file:
            db.session.delete(pdb_file)
            db.session.commit()
            return True
        return False