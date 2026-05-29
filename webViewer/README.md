
# WebViewer — README

Ce document décrit comment configurer et lancer l'application WebViewer sous Windows et Linux. Les instructions ci-dessous sont centrées sur un environnement Python isolé (virtualenv ou conda) et une base PostgreSQL optionnelle.

## Prérequis
- Python 3.9+
- pip ou conda
- PostgreSQL

Cloner le dépôt et se placer dans le dossier:

```bash
git clone https://github.com/MSitam14/InternshipTestProject
cd InternshipTestProject/webViewer
```

## Windows (virtualenv)

1. Créer et activer un environnement virtuel, puis installer les dépendances:

```bash
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. PostgreSQL — démarrage et création d'un utilisateur / base:

Dans PostgreSQL:

```sql
CREATE USER protein_viewer_user WITH PASSWORD 'protein';
CREATE DATABASE pdb_viewer OWNER protein_viewer_user;
GRANT ALL PRIVILEGES ON DATABASE pdb_viewer TO protein_viewer_user;
```

3. Démarrer l'application:

```bash
python manage.py runserver
# Accessible par défaut sur http://127.0.0.1:5000/
```

## Linux (conda recommandé)

1. Créer et activer un environnement conda:

```bash
conda create -n webviewer python=3.9 -y
conda activate webviewer
```

2. Installer les dépendances:

```bash
pip install -r requirements.txt
```

3. PostgreSQL — démarrage et création d'un utilisateur / base:

```bash
sudo service postgresql start
sudo -u postgres psql
```

Dans le shell PostgreSQL:

```sql
CREATE USER protein_viewer_user WITH PASSWORD 'protein';
CREATE DATABASE pdb_viewer OWNER protein_viewer_user;
GRANT ALL PRIVILEGES ON DATABASE pdb_viewer TO protein_viewer_user;
```

4. Initialiser la base puis lancer le serveur:

```bash
python manage.py init_db
python manage.py runserver
```



