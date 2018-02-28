import os
import random
import time
from flask import Flask, jsonify, request, abort, send_from_directory, Blueprint
from .cluster import Cluster
from ..models import Instance
from ..database import db_session



class DummyCluster(Cluster):    
    def __init__(self):
        super().__init__()

    def create_container(self):
        time.sleep(5)
        if not request.json or 'image' not in request.json:
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

    def confirm_launch(self):
        if not request.json or 'ui_url' not in request.json:
            abort(400)
        url = db_session.query(Instance).filter_by(ui_link = request.json['ui_url']).first()
        if url == None:
            return jsonify({"error" : "non-existant container"})
        return jsonify({"verified" : "confirmed"})    

    
