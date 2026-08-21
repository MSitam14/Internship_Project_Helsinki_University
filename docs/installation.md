# Installation

This document explains how to install and configure the project.

## Prerequisites

Before getting started, make sure you have:

* Conda (Miniconda or Anaconda)
* Python 3.9
* PostgreSQL
* A Linux environment

## 1. Clone the Repository

```bash
git clone https://github.com/MSitam14/InternshipTestProject
cd InternshipTestProject
```

## 2. Configure the `.env` File

Create a new `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Then edit the `.env` file and fill in the required environment variables.

## 3. Create the Conda Environment

```bash
conda env create -f requirements_webViewer.yml
```

## 4. Activate the Environment

```bash
conda activate webViewer
```

## 5. Start PostgreSQL

Start the PostgreSQL service:

```bash
sudo service postgresql start
```

Open the PostgreSQL shell:

```bash
sudo -u postgres psql
```

Create the database user and database using the values from your `.env` file:

```sql
CREATE USER DB_USER WITH PASSWORD 'DB_PASSWORD';

CREATE DATABASE DB_NAME OWNER DB_USER;

GRANT ALL PRIVILEGES ON DATABASE DB_NAME TO DB_USER;
```

Replace:

* `DB_USER`
* `DB_PASSWORD`
* `DB_NAME`

with the corresponding values from your `.env` file.

## 6. Initialize the Database

```bash
python manage.py init_db
```

> **Warning:** This command removes existing tables before recreating them. Do not use it on a database containing data you want to keep.

## Running the Application

Start the application from the project root:

```bash
python manage.py runserver
```

By default, the server runs at:

```text
http://127.0.0.1:5000
```
