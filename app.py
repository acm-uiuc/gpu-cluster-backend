from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging
from cw_libs import clearwaters_docker as cwd
import commands

app = Flask(__name__)
CORS(app)
PORT=5656
docker_client = cwd.CWDockerClient()
used_ports = 8889

@app.route('/create_container', methods=['POST'])
def update_acm_request():
    global used_ports
    if not request.json or 'image' not in request.json:
        abort(400)
    print(request.json['image'])
    print(used_ports)
    port = used_ports + 1
    used_ports = port
    print(used_ports)
    c_id = docker_client.create_container('', image = request.json['image'], is_gpu = True, port = port)
    token = docker_client.run_cmd(c_id, 'python ../jupyter_get.py')
    
    url = "http://vault.acm.illinois.edu:"+str(port)+"/?token="+str(token)
    print(url)
    return jsonify({'jupyter_url' : url})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
