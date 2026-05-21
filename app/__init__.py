from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
# from flask.ext.login import LoginManager
# from flask.ext.moment import Moment
# from flask.ext.pagedown import PageDown
# from flask.ext.mail import Mail
from config import config
import os
import sys
from config import basedir
import logging
from logging.handlers import RotatingFileHandler
import psycopg2


bootstrap = Bootstrap()
db = SQLAlchemy()
# moment = Moment()
# pagedown = PageDown()
# mail = Mail()
# login_manager = LoginManager()
# login_manager.login_view = 'viewer.login'


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
    # moment.init_app(app)
    # pagedown.init_app(app)
    # login_manager.init_app(app)
    from .viewer import viewer as viewer_blueprint
    from .viewer.api import api as api_blueprint
    app.register_blueprint(viewer_blueprint)
    app.register_blueprint(api_blueprint)
    return app