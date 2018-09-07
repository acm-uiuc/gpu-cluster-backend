from ..database import db_session
from ..models import Instance
from .container_controller import ContainerController
from nvdocker import NVDockerClient

class GPUContainerController(ContainerController):

    def __init__(self, config):
        super().__init__(config)
        self.docker_client = NVDockerClient()
    
    def create_container(image, user="", token_required=False, budget=-1, num_gpus=1):
        # Get 2 open ports for UI and Monitor
        uport = self.get_port()
        mport = self.get_port()
        while uport == mport:
            mport = self.get_port()

        # Get select a gpu(s) that are least in use
        num_available_gpus = len(docker_client.list_gpus())
        if num_gpus > num_available_gpus:
            num_gpus = num_available_gpus

        gpus = []
        memory_usage = docker_client.gpu_memory_usage()
        for g in num_gpus:
            for gpu, used in memory_usage.items():
                if used < memory_usage[gpu[-1]]:
                    gpus.append(gpu)

        # Assemble config for container 
        container_config = {
            "ports": {
                '8888/tcp': uport,
                '6006/tcp': mport
            },
            "working_dir": "/vault/" + user,
            "visible_devices": gpus,
            "detach": True,
            "auto_remove": True
        }

        #create container
        c_id = docker_client.create_container(image, **container_config).id

        #assemble endpoints for UI, monitor and get the access token if needed
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
        
        #TODO insert budget
        budget = -1 
        db_session.add(Instance(c_id, uport, mport, uurl, murl, user, budget, token))   
        db_session.commit()
        return c_id, uurl, murl

    def kill_container(self, c_id):
        self.docker_client.stop_container(c_id)