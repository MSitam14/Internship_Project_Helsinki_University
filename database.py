# """
# Configuration et modèles de la base de données.
# """

# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime

# db = SQLAlchemy()

# class PDBFile(db.Model):
#     """Modèle pour les fichiers PDB"""
#     __tablename__ = 'pdb_files'
    
#     id = db.Column(db.Integer, primary_key=True)
#     filename = db.Column(db.String(255), unique=True, nullable=False)
#     content = db.Column(db.Text, nullable=False)
    
#     def __repr__(self):
#         return f'<PDBFile {self.filename}>'

