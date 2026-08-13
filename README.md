# Installation & Run

Ce document décrit l’installation complète et le lancement du projet.

---

# Prérequis

Avant de commencer, assure-toi d’avoir :

- Conda (Miniconda ou Anaconda)
- Python 3.9
- postgresql
- Environement linux

---

# Installation complète

## 1. Cloner le dépôt et se placer dans le dossier:

```bash
git clone https://github.com/MSitam14/InternshipTestProject
cd InternshipTestProject
```

## 2. Remplire le .env

Copier le comptenu de .env.example dans un nouveau fichier .env <br>
Remplire le nouveau fichier .env


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

Dans le shell PostgreSQL (/.../ a remplir avec le .env ):

```sql
CREATE USER /DB_USER/ WITH PASSWORD /'DB_PASSWORD'/;
CREATE DATABASE /DB_NAME/ OWNER /DB_USER/;
GRANT ALL PRIVILEGES ON DATABASE /DB_NAME/ TO /DB_USER/;
```

## 6. Initialiser la base :

```bash
python manage.py init_db
```

---

# Lancement du projet
```bash
python manage.py runserver
```

