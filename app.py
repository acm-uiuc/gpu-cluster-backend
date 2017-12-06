from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging
from cw_libs import clearwaters_docker as cwd
import commands
from models import db, Ports
import random

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Docker_Ports.sqlite'

CORS(app)

db.init_app(app)
db.create_all(app=app)

PORT=5656
docker_client = cwd.CWDockerClient()

@app.route('/create_container', methods=['POST'])
def update_acm_request():
    if not request.json or 'image' not in request.json:
        abort(400)

    port = get_port()
    
    c_id = docker_client.create_container('', image = request.json['image'], is_gpu = True, port = port)
    token = docker_client.run_cmd(c_id, 'python ../jupyter_get.py')
    url = "http://vault.acm.illinois.edu:{}/?token={}".format(port, token)
    docker_port = Ports(port, url)
    db.session.add(docker_port)
    db.session.commit()
    
    return jsonify({'jupyter_url' : url})

def get_port():
    while True:
        rand_port = random.randint(80, 65535)
        used_ports = Ports.query.filter_by(port = rand_port)
        if (len(used_ports) == 0):
            return rand_ports
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
