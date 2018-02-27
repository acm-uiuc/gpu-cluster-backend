import argparse
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
import logging
from flask_sqlalchemy import SQLAlchemy
from models import InstanceAssigment, Base
import os
import random
import logging
import time
import yaml

parser = argparse.ArgumentParser(description="Stand up an easy to use UI for creating Deep Learning workspaces")
parser.add_argument('-p', '--port', type=int, default=5656, help='port to run the interface on')
parser.add_argument('-g', '--gpuless', action='store_true', help='if development is being done on a machine without a gpu')
args = parser.parse_args()

PORT=args.port
GPULESS = args.gpuless
DB_LOCATION = '/opt/gpu_cluster/gpu_cluster_instances.db'
with open("config.yml", 'r') as config_file:
    try:
        config = yaml.load(config_file)
        if "port" in config:
            if PORT == 5656 and config["port"] != 5656:
                PORT = config["port"]
        if "gpuless" in config:
            if GPULESS == False and config["gpuless"] == True:
                GPULESS = True
        if "db_location" in config:
            DB_LOCATION = config["db_location"]
    except yaml.YAMLError as exc:
        print(exc)
        pass

docker_client = None
if not GPULESS:
    import nvdocker
    docker_client = nvdocker.NVDockerClient()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_LOCATION

instance_store = SQLAlchemy(app)
CORS(app)

@app.before_first_request
def setup():
    # Recreate database each time for demo
    Base.metadata.drop_all(bind=instance_store.engine)
    Base.metadata.create_all(bind=instance_store.engine)

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>')
def serve_ui(path):
    return send_from_directory(os.path.dirname(os.path.realpath(__file__)) + "/frontend/build", 'index.html') 

@app.route('/create_container', methods=['POST'])
def create_container():
    if not request.json or 'image' not in request.json:
        abort(400)

    uport = get_port()
    mport = get_port()
    while uport == mport:
        mport = get_port()

    user = ""    
    if 'user' in request.json:
        user = request.json['user']

    token_needed = False
    if 'token_required' in request.json:
        token_needed = bool(request.json['token_required'])

    c_id = docker_client.create_container('', image = request.json['image'], is_gpu = True, ports = (uport,mport), user = user)
    
    uurl = ""
    murl = ""
    if token_needed: 
        token = docker_client.run_cmd(c_id, 'python3 /opt/cluster-container/jupyter_get.py')
        uurl = "http://vault.acm.illinois.edu:{}/?token={}".format(uport, token.decode("utf-8") )
        murl = "http://vault.acm.illinois.edu:" + str(mport)
    else:
        uurl = "http://vault.acm.illinois.edu:" + str(uport)
        murl = "http://vault.acm.illinois.edu:" + str(mport)
    
    instance_store.session.add(InstanceAssigment(uport, mport, uurl, murl, user))   
    instance_store.session.commit()
    return jsonify({'ui_url' : uurl, 'monitor_url': murl})

@app.route('/dummy_create_container', methods=['POST'])
def dummy_create_container():
    time.sleep(5)
    if not request.json or 'image' not in request.json:
        abort(400)

    uport = get_port()
    mport = get_port()
    while uport == mport:
        mport = get_port()

    user = ""    
    if 'user' in request.json:
        user = request.json['user']

    token_needed = False
    if 'token_required' in request.json:
        token_needed = bool(request.json['token_required'])
    
    uurl = ""
    murl = ""
    if token_needed: 
        uurl = "http://google.com"
        murl = "http://google.com"
    else:
        uurl = "http://google.com"
        murl = "http://google.com"
    
    instance_store.session.add(InstanceAssigment(uport, mport, uurl, murl, user))   
    instance_store.session.commit()
    return jsonify({'ui_url' : uurl, 'monitor_url': murl})

def get_port():
    while True:
        rand_port = random.randint(80, 65535)
        used_jports = instance_store.session.query(InstanceAssigment).filter_by(jupyter_port = rand_port).first()
        used_mports = instance_store.session.query(InstanceAssigment).filter_by(monitor_port = rand_port).first()
        if (used_jports == None) and (used_mports == None):
            return rand_port
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
