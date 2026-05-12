from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Response
from database import db, PDBFile

app = Flask(__name__)

# Configuration PostgreSQL (sans mot de passe)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/pdb_viewer'
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
    navigation = [
        {"href": "/upload", "caption": "Upload a file"},
        {"href": "/hello/1", "caption": "Page Hello 1"},
        {"href": "/hello/2", "caption": "Page Hello 2"},
        {"href": "/hello/3", "caption": "Page Hello 3"}
    ]
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
    global pdb_storage
    if file_id in pdb_storage:
        content, filename = pdb_storage[file_id]
        return Response(content, mimetype='chemical/x-pdb', headers={"Content-Disposition": f"attachment;filename={filename}"})
    return "Fichier non trouvé", 404

@app.route('/uploadFileInDB', methods=['POST'])
def uploadFile():
    global pdb_counter, pdb_storage
    the_file = request.files['the_file']
    tech = request.form.get('tech')
    file_content = the_file.read().decode('utf-8', errors='replace')
    
    # Stocker le fichier avec un ID
    pdb_id = pdb_counter
    pdb_counter += 1
    pdb_storage[pdb_id] = (file_content, the_file.filename)
    
    page = None
    match tech:
        case '3DMol': 
            page = 'fileInfo_3Dmol.html';
        case 'MolStar': 
            page = 'fileInfo_molstar.html';

    return render_template(
        page,
        filename=the_file.filename,
        content_type=the_file.content_type,
        file_content=file_content,
        techUsed=tech,
        pdb_id=pdb_id
    )

@app.route('/fileInfo/<int:file_id>')
def fileInfo(file_id):
    return f"File info page for file ID: {file_id}"

# Importer et enregistrer les routes API
from api import api
app.register_blueprint(api)
