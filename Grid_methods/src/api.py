import datetime
import json
import os
import base64
import shutil
from .main import main_api

from flask import Blueprint, request, jsonify

api = Blueprint('api-hot-comp', __name__, url_prefix='/api-hot-comp')


@api.route('/status', methods=['GET'])
def status():
    """GET /api-hot-comp/status - check the status of the API"""
    return jsonify({
        'status': 'success',
        'message': 'API is running'
    }), 200

def _json_safe(value):
    """Convert non-JSON values (notably bytes) into JSON-serializable values."""
    if isinstance(value, bytes):
        return {
            'encoding': 'base64',
            'data': base64.b64encode(value).decode('ascii')
        }
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value

# input: {  
#           "params": {"param1": "value1", "param2": "value2"}, 
#           "pdb1": {"name": "file1.pdb", "content": "PDB content 1"}, 
#           "pdb2": {"name": "file2.pdb", "content": "PDB content 2"}
#       }
@api.route('/comparison', methods=['POST'])
def calculate_comparison():
    """POST /api-hot-comp/comparison - calculate hot spot comparison"""
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    data = request.get_json()
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No input data provided'
        }), 400

    try:
        params = data['params']
        pdb1 = data['pdb1']
        pdb2 = data['pdb2']
    except KeyError as e:
        return jsonify({
            'status': 'error',
            'message': f'Missing parameter: {str(e)}'
        }), 400

    file_path = 'Grid_methods/data/input/structures/' + date + '/'
    pdb1_path = file_path + pdb1["name"]
    pdb2_path = file_path + pdb2["name"]

    params['comparison_parameters']["path_to_PDB_directory"] = file_path

    with open(pdb1_path, 'w') as f:
        f.write(pdb1["content"])
    
    with open(pdb2_path, 'w') as f:
        f.write(pdb2["content"])
    
    print(f"\nReceived comparison request for {pdb1['name']} and {pdb2['name']}")
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        out = main_api(params) 
    except Exception as e:
        shutil.rmtree(file_path)
        return jsonify({
            'status': 'error',
            'message': f'Error during comparison: {str(e)}'
        }), 400
    
    print(f"Comparison completed for {pdb1['name']} and {pdb2['name']}. Cleaning up temporary files.")
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")

    try: shutil.rmtree(file_path)
    except OSError: print(f"Directory '{file_path}' not found.")

    return jsonify({
        'status': 'success',
        'content': _json_safe(out)
    })