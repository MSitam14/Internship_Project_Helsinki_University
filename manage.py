#!/usr/bin/env python
import argparse
import os
from webViewer.app import create_app
from webViewer.app import db
from flask_migrate import Migrate


if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        if not line.strip() or line.strip().startswith('#'):
            continue
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

def main():
    parser = argparse.ArgumentParser(description='Project management commands')
    subparsers = parser.add_subparsers(dest='command')

    runserver_parser = subparsers.add_parser('runserver', help='Run development server')
    runserver_parser.add_argument('--host', default='127.0.0.1')
    runserver_parser.add_argument('--port', type=int, default=5000)
    runserver_parser.add_argument('--debug', action='store_true')

    subparsers.add_parser('init_db', help='Drop and recreate all tables')

    args = parser.parse_args()

    if args.command == 'runserver':
        app.run(host=args.host, port=args.port, debug=args.debug)
    elif args.command == 'init_db':
        init_db()
        print("Database initialized: all tables dropped and recreated.")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()