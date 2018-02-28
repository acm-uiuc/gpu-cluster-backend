import argparse
from flask import Flask, jsonify, request, abort, send_from_directory, Blueprint
from flask_cors import CORS
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from models import Instance, Base
import os
import random
import time
from db_connector import db_session

cluster_api = Blueprint('cluster_api', __name__)

@cluster_api.route('/create_container', methods=['POST'])
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
    
    #TODO insert budget

    db_session.add(Instance(uport, mport, uurl, murl, user, 0))   
    db_session.commit()
    return jsonify({'ui_url' : uurl, 'monitor_url': murl})

@cluster_api.route('/dummy_create_container', methods=['POST'])
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
    
    db_session.add(Instance(uport, mport, uurl, murl, user, 0))   
    db_session.commit()
    return jsonify({'ui_url' : uurl, 'monitor_url': murl})

@cluster_api.route('/confirm', methods=['POST'])
def confirm_launch():
    if not request.json or 'ui_url' not in request.json:
        abort(400)
    url = db_session.query(Instance).filter_by(ui_link = request.json['ui_url']).first()
    if url == None:
        return jsonify({"error" : "non-existant container"})
    return jsonify({"verified" : "confirmed"})    

def get_port():
    while True:
        rand_port = random.randint(80, 65535)
        used_jports = db_session.query(Instance).filter_by(ui_port = rand_port).first()
        used_mports = db_session.query(Instance).filter_by(monitor_port = rand_port).first()
        if (used_jports == None) and (used_mports == None):
            return rand_port
