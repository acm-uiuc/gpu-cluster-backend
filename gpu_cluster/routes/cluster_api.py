import os
import random
import time
from ..database import db_session
from ..models import Instance
from flask import Flask, jsonify, request, abort 

class ClusterAPI():
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def create_container(self):
        if not request.json:
            abort(400)

        for f in  ["image", "token_required"]: #,"user", "budget"]
            if f not in request.json: 
                abort(400)

        cid, ui_url, murl = self.controller.create_container(request.json['image'],  token_required=request.json['token_required'])#, user=request.json['user'], budget=request.json['budget'] )
        return jsonify({'cid': cid, 'ui_url' : ui_url, 'monitor_url': murl})

    def confirm_launch(self):
        if not request.json or 'cid' not in request.json:
            abort(400)        
        
        launched = self.controller.launch_container(request.json["cid"])

        if launched == False:
            return jsonify({"error" : "non-existant container"})
        return jsonify({"verified" : "confirmed"})    

    def kill_container(self):
        pass

    def register_routes(self, app):
        app.add_url_rule('/create_container', 'create_container', self.create_container, methods=['POST'])
        app.add_url_rule('/confirm',          'confirm',          self.confirm_launch,   methods=['POST'])
        app.add_url_rule('/kill_container',   'kill_container',   self.kill_container,   methods=['POST'])

