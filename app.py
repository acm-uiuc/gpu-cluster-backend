from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging
from cw_libs import clearwaters_docker as cwd
import commands

app = Flask(__name__)
CORS(app)
PORT=5656
docker_client = cwd.CWDockerClient()

@app.route('/create_container', methods=['POST'])
def update_acm_request():
    if not request.json or 'image' not in request.json:
        abort(400)
    print(request.json['image'])
    c_id = docker_client.create_container('', image = request.json['image'], is_gpu = True)
    #c_logs = docker_client.get_container_logs(c_id)
    c_logs = commands.getoutput('sudo docker logs '+c_id)
    '''
    while c_logs == '':
        c_logs = docker_client.get_container_logs(c_id)
        print(c_logs)    
    '''
    print(c_logs)
    return jsonify({'container_id' : c_id})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
