from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
import os


bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config.from_object(config[config_name])
    if os.environ.get('HEROKU') is not None:
        import logging
        stream_handler = logging.StreamHandler()
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('intership project')
    bootstrap.init_app(app)
    db.init_app(app)
    from webViewer.app.viewer import viewer as viewer_blueprint
    from webViewer.app.viewer.api import api as api_viewer_blueprint
    from Fitness_score.src.api import api as api_score_blueprint
    app.register_blueprint(viewer_blueprint)
    app.register_blueprint(api_viewer_blueprint)
    app.register_blueprint(api_score_blueprint)
    return app