
## Installation

Create .venv
```
py -3 -m venv .venv
```

Activate .venv
```
.venv\Scripts\activate
```

Install dependencies
```
pip install Flask Flask-SQLAlchemy psycopg2-binary
```

## Database Setup

**Prerequisites:**
- PostgreSQL must be installed and running
- Default credentials: user=`postgres`, password=`admin`

Create the database
```
createdb -U postgres -h localhost pdb_viewer
```

Initialize the database tables
```
python init_db.py
```

## Start

Run the Flask application
```
flask run
```

Run with debug mode
```
flask run --debug
```