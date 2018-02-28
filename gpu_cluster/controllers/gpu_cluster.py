import os
import random
import time
from flask import Flask, jsonify, request, abort, send_from_directory, Blueprint
from .cluster import Cluster
from ..models import Instance
from ..nvdocker import nvdocker
from ..database import db_session

class GPUCluster(Cluster):
    docker_client = None 

    def __init__(self):
        super().__init__()
        docker_client = nvdocker.NVDockerClient()
        
    def create_container(self):
        if not request. json or 'image' not in request.json:
            abort(400)

        uport = self.get_port()
        mport = self.get_port()
        while uport == mport:
            mport = self.get_port()

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

    def confirm_launch():
        if not request.json or 'ui_url' not in request.json:
            abort(400)
        url = db_session.query(Instance).filter_by(ui_link = request.json['ui_url']).first()
        if url == None:
            return jsonify({"error" : "non-existant container"})
        return jsonify({"verified" : "confirmed"})    