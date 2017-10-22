from flask import Flask, jsonify, request, abort
import logging
from cw_libs import clearwaters_docker as cwd

app = Flask(__name__)
PORT=5656

images = {
    'TensorFlow': 'registry.gitlab.com/acm_uiuc/gpu-cluster-images:tensorflow',
    'TensorFlow': 'registry.gitlab.com/acm_uiuc/gpu-cluster-images:caffe2',
    'TensorFlow': 'registry.gitlab.com/acm_uiuc/gpu-cluster-images:pytorch',
    'Keras': 'registry.gitlab.com/acm_uiuc/gpu-cluster-images:keras',
    'Digits': 'nvidia/digits',
    'Caffe': 'nvidia/caffe'
}

@app.route('/create_container', methods=['PUT'])
def update_acm_request():
    if not request.json or 'image' not in request.json:
        abort(400)
    c_id = cwd.create_container('', image = images[image], is_gpu = True)
    return jsonify({'container_id' : c_id})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
