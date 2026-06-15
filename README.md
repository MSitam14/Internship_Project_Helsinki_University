# Installation & Run

Ce document décrit l’installation complète et le lancement du projet.

---

# Prérequis

Avant de commencer, assure-toi d’avoir :

- Conda (Miniconda ou Anaconda)
- Python 3.11+
- Environement linux

---

# Installation complète

## 1. Cloner le dépôt et se placer dans le dossier:

```bash
git clone https://github.com/MSitam14/InternshipTestProject
cd InternshipTestProject
```

## 2. Remplire le .env


## 3. Créer l’environnement Conda

```bash
conda env create -f requirements_webViewer.yml
```

## 4. Activer l’environnement

```bash
conda activate webViewer
```

## 5. PostgreSQL — démarrage et création d'un utilisateur / base:

```bash
sudo service postgresql start
sudo -u postgres psql
```

Dans le shell PostgreSQL (/.../ to fil):

```sql
CREATE USER /user/ WITH PASSWORD /'password'/;
CREATE DATABASE pdb_viewer OWNER /user/;
GRANT ALL PRIVILEGES ON DATABASE pdb_viewer TO /user/;
```

## 6. Initialiser la base :

```bash
python manage.py init_db
```

---

# Lancement du projet
```bash
cd src
python manage.py runserver
```

