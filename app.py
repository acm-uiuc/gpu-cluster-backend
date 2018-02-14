from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
import logging
import nvdocker
from flask_sqlalchemy import SQLAlchemy
from models import InstanceAssigment, Base
import os
import random

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/gpu_cluster/gpu_cluster_instances.db'

instance_store = SQLAlchemy(app)
CORS(app)
PORT=4000
docker_client = nvdocker.NVDockerClient()

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

    jport = get_port()
    mport = get_port()
    while jport == mport:
        mport = get_port()

    user = ""    
    if 'user' in request.json:
        user = request.json['user']

    c_id = docker_client.create_container('', image = request.json['image'], is_gpu = True, ports = (jport,mport), user = user)
    token = docker_client.run_cmd(c_id, 'python3 /opt/cluster-container/jupyter_get.py')
    jurl = "http://vault.acm.illinois.edu:{}/?token={}".format(jport, token.decode("utf-8") )
    murl = "http://vault.acm.illinois.edu:" + str(mport)
    instance_store.session.add(InstanceAssigment(jport, mport, jurl, murl, user))   
    instance_store.session.commit()
    return jsonify({'jupyter_url' : jurl, 'monitor_url': murl})

def get_port():
    while True:
        rand_port = random.randint(80, 65535)
        used_jports = instance_store.session.query(InstanceAssigment).filter_by(jupyter_port = rand_port).first()
        used_mports = instance_store.session.query(InstanceAssigment).filter_by(monitor_port = rand_port).first()
        if (used_jports == None) and (used_mports == None):
            return rand_port
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
