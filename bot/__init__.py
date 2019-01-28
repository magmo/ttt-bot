from os import environ, getcwd, path
from threading import Thread
from time import sleep

import firebase_admin
from flask import Flask, g, request
from flask.logging import logging

from bot import challenge
from bot.config import get_project
from bot.util import hex_to_str

def get_fb_project_name(app):
    if app.config['TESTING']:
        environ["GOOGLE_APPLICATION_CREDENTIALS"] = path.join(getcwd(), 'creds_test.json')
        return 'rock-paper-scissors-test'
    return get_project()

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    app.logger.setLevel(logging.INFO)
    @app.before_request
    def _log_request_info():
        app.logger.debug(f'Headers: {request.headers}')
        app.logger.debug(f'Body: {request.get_data()}')

    @app.before_request
    def _set_bot_addr():
        request_json = request.get_json()
        g.bot_addr = hex_to_str(request_json.get('address_key')).lower()

    try:
        firebase_admin.get_app()
    except ValueError:
        project_name = get_fb_project_name(app)
        firebase_admin.initialize_app(options={
            'databaseURL': f'https://{project_name}.firebaseio.com',
            'projectId': project_name
        })


    from bot import player
    app.register_blueprint(player.BP)
    return app
