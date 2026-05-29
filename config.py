import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or '\xbb\xed\x0e?\xcfY#8Ev\x17\
    x04t\x15\xa4\x8b\xa8\****************'
    USER_PER_PAGE = 10
    if os.environ.get('DATABASE_URL') is None:
        db_user = 'protein_viewer_user'
        db_password = 'protein'
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                 f'postgresql://{db_user}:{db_password}@localhost:5432/pdb_viewer?client_encoding=utf8')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
        SQLALCHEMY_RECORD_QUERIES = True
    print(SQLALCHEMY_DATABASE_URI)


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False


class HerokuConfig(ProductionConfig):
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}