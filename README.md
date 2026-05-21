

## Set up
------------
**Step 1**: Clone the git repository

    $ https://github.com/MSitam14/InternshipTestProject
    $ cd InternshipTestProject

**Step 2**: Create a virtual environment

    $ py -3 -m venv .venv
    $ .venv\Scripts\activate
    (venv) $ pip install -r requirements.txt

**Step 4**: Start the application:

    (venv) $ python manage.py runserver
     * Running on http://127.0.0.1:5000/


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