from flask import Blueprint
viewer = Blueprint('viewer', __name__)
from . import routes, api
