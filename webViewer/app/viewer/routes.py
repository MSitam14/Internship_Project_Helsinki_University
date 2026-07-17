from flask import render_template, flash, redirect, \
    url_for, abort, request, current_app
from ..static.tools.viewer.RequestParamFitness import AtomType
from ..static.tools.viewer.RequestParamFitness import RequestParamFitness
from ..import db
from ..models import TempSaveScoreOneFile
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

    return render_template('viewer/index.html', a_variable='Home Page')

@viewer.route('/fitnessForm', methods=['GET'])
def fitnessForm():
    return render_template('viewer/fitnessForm.html')

@viewer.route('/pdbInfo')
def pdbInfo(parameters):

    return render_template(
        'viewer/proteinInfo.html',
        params=parameters
    )

@viewer.route('/pdbInfoUserKey', methods=['POST'])
def pdbInfoParameters():
    
    userKey = request.form.get('userKey')

    data = TempSaveScoreOneFile.get_by_user_key(userKey)

    if not data:
        return fitnessForm()
    
    else:
        parameters = data.parameter
    
        return pdbInfo((parameters))

@viewer.route('/pdbInfoRequest', methods=['POST'])
def pdbInfoRequest():
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
    
    return pdbInfo(json.loads(params.toJson()))

@viewer.errorhandler(404)
def page_not_found(error):
    return render_template('viewer/pageNotFound.html', error=error), 404