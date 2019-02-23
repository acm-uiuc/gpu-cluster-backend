from ..database import db_session
from ..models import Instance
from .container_controller import ContainerController
from nvdocker import NVDockerClient

class GPUContainerController(ContainerController):

    def __init__(self, config):
        super().__init__(config)
        self.config = config;
        self.docker_client = NVDockerClient()
    
    def create_container(self, image, user="", token_required=False, budget=-1, num_gpus=1):
        if NVDockerClient.least_used_gpu() == None :
            #TODO Add handle multi node functionality here
            pass
        
        # Get 2 open ports for UI and Monitor
        uport = super().get_port()
        mport = super().get_port()
        while uport == mport:
            mport = super().get_port()

        # Get select a gpu(s) that are least in use
        num_available_gpus = len(NVDockerClient.gpu_info())
        if num_gpus > num_available_gpus:
            num_gpus = num_available_gpus

        gpus = []
        for g in range(num_gpus):
            if NVDockerClient.gpu_memory_usage(g)["free_mb"] > 0:
                gpus.append(g)
                
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
        c_id = self.docker_client.create_container(image, **container_config).id

        #assemble endpoints for UI, monitor and get the access token if needed
        uurl = ""
        murl = ""
        token = ""
        if token_required: 
            token = self.docker_client.exec_run(c_id, 'python3 /opt/cluster-container/jupyter_get.py')
            base_url = "http://{}".format(self.config["domain_name"])
            uurl = "{}:{}/?token={}".format(base_url, uport, token.decode("utf-8") )
            murl = base_url + str(mport)
        else:
            uurl = base_url + str(uport)
            murl = base_url + str(uport)
        
        #TODO insert budget
        budget = -1 
        db_session.add(Instance(c_id, uport, mport, uurl, murl, user, budget, token))   
        db_session.commit()
        return c_id, uurl, murl

    def kill_container(self, c_id):
        self.docker_client.stop_container(c_id)
