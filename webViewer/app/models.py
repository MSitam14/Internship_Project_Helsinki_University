"""
Configuration et modèles
"""

from . import db

from datetime import datetime, timedelta
import random
import string

class TempSaveScoreOneFile(db.Model):
    """Modèle pour le stockage temporaire des scores"""
    __tablename__ = 'temp_save_score_one_file'
    
    __table_args__ = (
        db.Index('idx_user_key', 'user_key'),
        db.Index('idx_last_used', 'date_last_used'),
    )
    
    user_key = db.Column(db.String(16), primary_key=True)
    parameter = db.Column(db.JSON, nullable=False)
    cif_file_name = db.Column(db.String(255), nullable=False)
    cif_file_content = db.Column(db.Text, nullable=False)
    csv_file_name = db.Column(db.String(255), nullable=False)
    csv_file_content = db.Column(db.Text, nullable=False)
    date_last_used = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<TempSaveScoreOneFile {self.user_key}>'
    
    @staticmethod
    def clean_old_entries():
        """Supprime les entrées plus anciennes que le nombre de jours spécifié"""
        threshold_date = datetime.now() - timedelta(minutes=30)
        old_entries = TempSaveScoreOneFile.query.filter(TempSaveScoreOneFile.date_last_used < threshold_date).all()
        for entry in old_entries:
            db.session.delete(entry)
        db.session.commit()
    
    @staticmethod
    def get_by_user_key(userKey):

        TempSaveScoreOneFile.clean_old_entries()

        """Récupère les données de score par user_key"""

        data = TempSaveScoreOneFile.query.filter_by(user_key=userKey).first()

        data.date_last_used = datetime.now()

        db.session.commit()

        return data
    
    @staticmethod
    def user_key_exists(userKey):
        """Vérifie si un user_key existe dans la table"""
        return db.session.query(TempSaveScoreOneFile.query.filter_by(user_key=userKey).exists()).scalar()
    
    @staticmethod
    def save_score_data(userKey ,parameter, cif_file_name, cif_file_content, csv_file_name, csv_file_content):

        TempSaveScoreOneFile.clean_old_entries()

        """Sauvegarde les données de score dans la BD"""
        if(TempSaveScoreOneFile.user_key_exists(userKey)):
            # Mettre à jour l'entrée existante
            score_data = TempSaveScoreOneFile.get_by_user_key(userKey)
            score_data.parameter = parameter
            score_data.cif_file_name = cif_file_name
            score_data.cif_file_content = cif_file_content
            score_data.csv_file_name = csv_file_name
            score_data.csv_file_content = csv_file_content
            score_data.date_last_used = datetime.now()
        else:
            # Créer une nouvelle entrée
            score_data = TempSaveScoreOneFile(
                user_key=userKey,
                parameter=parameter,
                cif_file_name=cif_file_name,
                cif_file_content=cif_file_content,
                csv_file_name=csv_file_name,
                csv_file_content=csv_file_content,
                date_last_used=db.func.now()
            )
            db.session.add(score_data)
        db.session.commit()

    @staticmethod
    def generate_user_key():
        """Génère un user_key unique"""
        
        while True:
            userKey = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            if not TempSaveScoreOneFile.user_key_exists(userKey):
                return userKey
         
