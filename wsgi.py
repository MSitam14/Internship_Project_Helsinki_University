import os
from webViewer.app import create_app

# Create a Flask application instance using the factory function

app = create_app(os.environ.get('FLASK_CONFIG', 'production'))