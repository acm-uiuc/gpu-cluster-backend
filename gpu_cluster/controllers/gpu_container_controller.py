from ..database import db_session
from ..models import Instance
from .container_controller import ContainerController
from nvdocker import NVDockerClient

class GPUContainerController(ContainerController):

    def __init__(self, config):
        super().__init__(config)
        self.docker_client = NVDockerClient()
    
    def create_container(image, user="", token_required=False, budget=-1):
        uport = self.get_port()
        mport = self.get_port()
        while uport == mport:
            mport = self.get_port()

        container_config = {
            "ports": {
                '8888/tcp': uport,
                '6006/tcp': mport
            },
            "working_dir": "/vault",
            "visible_devices": 0,
            "detach": True,
            "auto_remove": True
        }

        c_id = docker_client.create_container(image, **container_config)

        uurl = ""
        murl = ""
        token = ""
        if token_required: 
            token = docker_client.exec_run(c_id, 'python3 /opt/cluster-container/jupyter_get.py')
            uurl = "http://vault.acm.illinois.edu:{}/?token={}".format(uport, token.decode("utf-8") )
            murl = "http://vault.acm.illinois.edu:" + str(mport)
        else:
            uurl = "http://vault.acm.illinois.edu:" + str(uport)
            murl = "http://vault.acm.illinois.edu:" + str(mport)
        
        print(image)
        #TODO insert budget
        budget = -1 
        db_session.add(Instance(c_id, uport, mport, uurl, murl, user, budget, token))   
        db_session.commit()
        return c_id, uurl, murl

    def kill_container(self, c_id):
        self.docker_client.stop_container(c_id)