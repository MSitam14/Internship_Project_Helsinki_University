"""
Script pour initialiser la base de données.

Usage:
    python init_db.py
"""

from app import app, db
from database import PDBFile

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Supprimer les tables existantes (optionnel, à utiliser avec précaution)
        print("Création des tables...")
        db.create_all()
        print("Base de données initialisée !")

        print("\nConfiguration :")
        print(f"  URI : {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\n Prêt à utiliser !")
