from flask import render_template, flash, redirect, \
    url_for, abort, request, current_app
from webViewer.app.static.tools.viewer.RequestParamGrid import RequestGridComparisonParameters
from webViewer.app.static.tools.viewer.RequestParamGrid import RequestGridHotspotParameters
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
    return redirect(url_for('viewer.home'))

@viewer.route('/home')
def home():

    return render_template('viewer/home.html')

@viewer.route('/fitnessForm', methods=['GET'])
def fitnessForm():
    return render_template('viewer/fitnessForm.html')

@viewer.route('/pdbInfo')
def pdbInfo(parameters):

    return render_template(
        'viewer/scoreProteinInfo.html',
        params=parameters
    )

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

@viewer.route('/requestFormComparison', methods=['GET'])
def requestFormComparison():
    return render_template('viewer/comparisonForm.html')

@viewer.route('/infoComparison', methods=['POST'])
def infoComparison(parameters):

    return render_template(
        'viewer/comparisonInfo.html',
        params=parameters
    )

@viewer.route('/infoComparisonRequest', methods=['POST'])
def infoComparisonRequest():

    params = RequestGridComparisonParameters()
    params.pdbList = {}

    files = request.files.getlist("files")

    for file in files:
        params.pdbList[file.filename] = file.read().decode('utf-8', errors='replace')

    params.grid_spacing = str(request.form.get('grid_spacing'))
    params.pocket_res_name = request.form.get('pocket_res_name') if request.form.get('pocket_res_name') != "" else "False"
    params.pocket_res_id = request.form.get('pocket_res_id')
    params.lig_chain = request.form.get('lig_chain') if request.form.get('lig_chain') != "" else "False"
    params.pocket_size = str(request.form.get('pocket_size'))
    params.discard_hetatm = "True" if request.form.get('discard_hetatm') else "False"
    params.discard_hydrogen = "True" if request.form.get('discard_hydrogen') else "False"
    params.discard_water = "True" if request.form.get('discard_water') else "False"
    params.keep_chains = request.form.get('keep_chains')

    params.consider_elements = "True" if request.form.get('consider_elements') else "False"
    params.tmalign_reference = request.form.get('tmalign_reference') if request.form.get('tmalign_reference') else "False"

    return infoComparison(json.loads(params.toJson()))

@viewer.route('/requestFormHotSpots', methods=['GET'])
def requestFormHotSpots():
    return render_template('viewer/hotSpotsForm.html')

@viewer.route('/infoHotSpots', methods=['POST'])
def infoHotSpots(parameters):

    return render_template(
        'viewer/hotSpotsInfo.html',
        params=parameters
    )

@viewer.route('/infoHotSpotsRequest', methods=['POST'])
def infoHotSpotsRequest():

    the_file = request.files['the_file']
    file_content = the_file.read().decode('utf-8', errors='replace')

    hotspot_type = request.form.getlist('hotspot_type') if request.form.getlist('hotspot_type') else ['None']
    hotspot_type = " ".join(hotspot_type)

    params = RequestGridHotspotParameters()

    params.pdb_name = the_file.filename
    params.pdb_content = file_content

    params.grid_spacing = str(request.form.get('grid_spacing'))
    params.pocket_res_name = request.form.get('pocket_res_name') if request.form.get('pocket_res_name') != "" else "False"
    params.pocket_res_id = request.form.get('pocket_res_id')
    params.lig_chain = request.form.get('lig_chain') if request.form.get('lig_chain') != "" else "False"
    params.pocket_size = str(request.form.get('pocket_size'))
    params.discard_hetatm = "True" if request.form.get('discard_hetatm') else "False"
    params.discard_hydrogen = "True" if request.form.get('discard_hydrogen') else "False"
    params.discard_water = "True" if request.form.get('discard_water') else "False"
    params.keep_chains = request.form.get('keep_chains')

    params.max_neighbor_number = str(request.form.get('max_neighbor_number'))
    params.tag_threshold = str(request.form.get('tag_threshold'))
    params.bad_score_threshold = str(request.form.get('bad_score_threshold'))
    params.good_score_threshold = str(request.form.get('good_score_threshold'))
    params.number_of_rounds = str(request.form.get('number_of_rounds'))

    params.hotspot_type = hotspot_type

    return infoHotSpots(json.loads(params.toJson()))


@viewer.route('/credits')
def credits():
    return render_template('viewer/credits.html')

@viewer.errorhandler(404)
def page_not_found(error):
    return render_template('viewer/pageNotFound.html', error=error), 404