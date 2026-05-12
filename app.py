from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Response
from database import db, PDBFile
import os
from urllib.parse import quote_plus

# Importer et enregistrer les routes API
from api import *

app = Flask(__name__)
app.register_blueprint(api)

os.environ['PGCLIENTENCODING'] = 'UTF8'

db_user = 'postgres'
db_password = quote_plus('admin')
db_host = 'localhost'
db_port = '5432'
db_name = 'pdb_viewer'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?client_encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser la BD avec l'app
db.init_app(app)

# Stockage temporaire des fichiers PDB 
pdb_storage = {}
pdb_counter = 0

@app.route('/')
def base():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    navigation = []

    all_pdb_files = get_all_files()

    for pdb_file in all_pdb_files:
        navigation.append({"href": f"/fileInfo/{pdb_file.id}/3DMol", "caption": f"{pdb_file.filename} (3Dmol)"})
        navigation.append({"href": f"/fileInfo/{pdb_file.id}/MolStar", "caption": f"{pdb_file.filename} (MolStar)"})

    return render_template('index.html', a_variable='The index page', navigation=navigation)

@app.route('/hello/')
@app.route('/hello/<int:hello_id>')
def hello(hello_id = 0):
    return f'Hello page : {hello_id}'

@app.route('/uploadPage')
def uploadPage():
    return render_template('upload.html')

@app.route('/pdb_content/<int:file_id>')
def pdb_content(file_id):

    pdb_file = get_file_by_id(file_id)

    if pdb_file is not None:
        return Response(pdb_file.content, mimetype='chemical/x-pdb', headers={"Content-Disposition": f"attachment;filename={pdb_file.filename}"})
    return "Fichier non trouvé", 404

@app.route('/uploadFileInDB', methods=['POST'])
def uploadFile():
    the_file = request.files['the_file']
    tech = request.form.get('tech')
    file_content = the_file.read().decode('utf-8', errors='replace')
    
    pdb_file = save_pdb_file(the_file.filename, file_content)

    return redirect(url_for('fileInfo', file_id=pdb_file.id, tech=tech))

@app.route('/fileInfo/<int:file_id>/<string:tech>')
def fileInfo(file_id, tech = '3DMol'):

    pdb_file = get_file_by_id(file_id)

    page = None
    match tech:
        case '3DMol': 
            page = 'fileInfo_3Dmol.html';
        case 'MolStar': 
            page = 'fileInfo_molstar.html';

    return render_template(
        page,
        filename=pdb_file.filename,
        file_content=pdb_file.content,
        techUsed=tech,
        pdb_id=pdb_file.id
    )


