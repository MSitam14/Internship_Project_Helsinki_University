from flask import render_template, flash, redirect, \
    url_for, abort, request, current_app
from ..import db
from ..models import PDBFile
from . import viewer
from flask import Response
from sqlalchemy.exc import IntegrityError



@viewer.route("/", defaults={"page": 1})

@viewer.route('/')
def base():
    return redirect(url_for('viewer.index'))

@viewer.route('/index')
def index():
    navigation = []

    all_pdb_files = PDBFile.get_all_files()

    for pdb_file in all_pdb_files:
        navigation.append({"id": f"{pdb_file.id}", "name": f"{pdb_file.filename}"})

    return render_template('viewer/index.html', a_variable='Index', navigation=navigation)

@viewer.route('/uploadPage')
def uploadPage():
    return render_template('viewer/upload.html')

@viewer.route('/pdb_content/<int:file_id>')
def pdb_content(file_id):

    pdb_file = PDBFile.get_file_by_id(file_id)

    if pdb_file is not None:
        return Response(pdb_file.content, mimetype='chemical/x-pdb', headers={"Content-Disposition": f"attachment;filename={pdb_file.filename}"})
    return "Fichier non trouvé", 404

@viewer.route('/uploadFileInDB', methods=['POST'])
def uploadFile():
    the_file = request.files['the_file']
    tech = request.form.get('tech')
    file_content = the_file.read().decode('utf-8', errors='replace')

    pdb_file = None
    try:
        pdb_file = PDBFile.save_pdb_file(the_file.filename, file_content)
    except IntegrityError as e:
        db.session.rollback()
        pdb_file = PDBFile.get_file_by_name(the_file.filename)
        if pdb_file is None:
            return "Erreur : le fichier existe mais n'a pas pu être récupéré", 500

    return redirect(url_for('viewer.fileInfo', file_id=pdb_file.id, tech=tech))

@viewer.route('/fileInfo/<int:file_id>/<string:tech>')
def fileInfo(file_id, tech = '3DMol'):

    pdb_file = PDBFile.get_file_by_id(file_id)

    page = None
    match tech:
        case '3DMol': 
            page = 'viewer/fileInfo_3Dmol.html'
        case 'MolStar': 
            page = 'viewer/fileInfo_molstar.html'
        case 'JSmol': 
            page = 'viewer/fileInfo_jsmol.html'

    return render_template(
        page,
        filename=pdb_file.filename,
        file_content=pdb_file.content,
        techUsed=tech,
        pdb_id=pdb_file.id
    )

@viewer.errorhandler(404)
def page_not_found(error):
    return render_template('viewer/pageNotFound.html', error=error), 404