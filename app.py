import argparse
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
from celery import Celery
import logging
from flask_sqlalchemy import SQLAlchemy
from models import Instance, Base
import os
import random
import logging
import time
import yaml
from cluster_api import cluster_api
from db_connector import init_db, db_session
from config import config

'''
Parse any command line arguments
'''
parser = argparse.ArgumentParser(description="Stand up an easy to use UI for creating Deep Learning workspaces")
parser.add_argument('-p', '--port', type=int, default=5656, help='port to run the interface on')
parser.add_argument('-g', '--gpuless', action='store_true', help='if development is being done on a machine without a gpu')
args = parser.parse_args()

PORT=args.port
GPULESS = args.gpuless
'''
Fill in any other unconfigured settings with config.yml fields
'''

if "port" in config:
    if PORT == 5656 and config["port"] != 5656:
        PORT = config["port"]
if "gpuless" in config:
    if GPULESS == False and config["gpuless"] == True:
        GPULESS = True

'''
Only import nvdocker if there are gpus to run with
'''
docker_client = None
if not GPULESS:
    import nvdocker
    docker_client = nvdocker.NVDockerClient()

'''
Suppress Logging to the terminal
'''
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

'''
Create app
'''
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + config["db"]
app.config['CELERY_BROKER_URL'] = config["redis"]
app.config['CELERY_RESULT_BACKEND'] = config["redis"]


celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


app.register_blueprint(cluster_api)

CORS(app)

@app.before_first_request
def setup():
    init_db()

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>')
def serve_ui(path):
    return send_from_directory(os.path.dirname(os.path.realpath(__file__)) + "/frontend/build", 'index.html') 


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
