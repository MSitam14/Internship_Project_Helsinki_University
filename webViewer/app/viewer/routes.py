from flask import render_template, flash, redirect, \
    url_for, abort, request, current_app
from ..static.tools.viewer.RequestParamFitness import AtomType
from ..static.tools.viewer.RequestParamFitness import RequestParamFitness
from ..import db
from ..models import PDBFile
from . import viewer
from flask import Response
from sqlalchemy.exc import IntegrityError
import requests
import json


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

    return render_template(
        'viewer/fileInfo.html',
        filename=pdb_file.filename,
        file_content=pdb_file.content,
        techUsed=tech,
        pdb_id=pdb_file.id
    )

@viewer.route('/proteinViewer/<string:tech>', methods=['POST'])
def proteinViewer(tech = '3DMol'):

    data = request.form.get('json')

    data = json.loads(data)

    fileName = data["file_name"]
    fileContent = data["file_content"]

    #todo regler id et nettoyer le code

    return render_template(
        'viewer/fileInfo.html',
        filename=fileName,
        file_content=fileContent,
        techUsed=tech,
        pdb_id=1
    )



@viewer.route('/fitnessForm', methods=['GET'])
def fitnessForm():
    return render_template('viewer/fitnessForm.html')

@viewer.route('/pdbInfo', methods=['POST'])
def pdbInfo():
    the_file = request.files['the_file']
    file_content = the_file.read().decode('utf-8', errors='replace')

    params = RequestParamFitness(
        pdb_name=the_file.filename,
        pdb_content=file_content,
        run_frequencies=request.form.get('run_frequencies') == 'on',
        water_env=request.form.get('water_env') == 'on',
        atom_type=AtomType(request.form.get('atom_type')),
        environment_size=int(request.form.get('environment_size')),
        pocket_num=request.form.get('pocket_num') if request.form.get('pocket_num') else None,
        model_num=int(request.form.get('model_num')))

    return render_template(
        'viewer/pdbInfo.html',
        params=params.toJson()
    )

@viewer.errorhandler(404)
def page_not_found(error):
    return render_template('viewer/pageNotFound.html', error=error), 404