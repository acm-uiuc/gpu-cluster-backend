# -*- coding: utf-8 -*-
'''
Copyright © 2017, ACM@UIUC
GPU Cluster Project is open source software, released under the University of
Illinois/NCSA Open Source License.  You should have received a copy of
this license in a file with the distribution.
'''

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging
import nvdocker
from flask_sqlalchemy import SQLAlchemy
from models import InstanceAssigment, Base
import requests
from Crypto.PublicKey import RSA
from Crypto import Random
import random

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/gpu_cluster/gpu_cluster_instances.db'
 
instance_store = SQLAlchemy(app)
CORS(app)
PORT=5656
docker_client = nvdocker.NVDockerClient()


random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
pub_key = key.publickey().exportKey()

@app.before_first_request
def setup():
    # Recreate database each time for demo
    Base.metadata.drop_all(bind=instance_store.engine)
    Base.metadata.create_all(bind=instance_store.engine)

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
    jurl = "http://vault.acm.illinois.edu:{}/?token={}".format(jport, token.decode("utf-8"))
    murl = "http://vault.acm.illinois.edu:" + str(mport)
    instance_store.session.add(InstanceAssigment(jport, mport, jurl, murl, user))   
    instance_store.session.commit()
    return jsonify({'jupyter_url' : jurl, 'monitor_url': murl})

@app.route('/session', methods=['POST'])
def transfer_session():
    if not request.json or 'token' not in request.json:
        abort(400)

    client_authorization = verify_session(request.json['token'])


    return jsonify(client_authorization)

@app.route('/pubkey', methods=['GET'])
def get_public_key():
    return jsonify({'pub_key':pub_key.decode("utf-8")})

def verify_session(token):
    session_token = key.decrypt(token)
    headers = {
        'Authorization': config.GROOT_TOKEN,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        "validationFactors": [{
            "value": "127.0.0.1",
            "name": "remote_address"
        }]
    }
    
    resp = requests.post('https://api.acm.illinois.edu/session/'+session_token, header=headers, body=payload)
    if resp.status_code != 200:
       return False

    if resp.json['token'] in resp.json:
        return True
    else:
        return False

def get_port():
    while True:
        rand_port = random.randint(80, 65535)
        used_jports = instance_store.session.query(InstanceAssigment).filter_by(jupyter_port = rand_port).first()
        used_mports = instance_store.session.query(InstanceAssigment).filter_by(monitor_port = rand_port).first()
        if (used_jports == None) and (used_mports == None):
            return rand_port
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)