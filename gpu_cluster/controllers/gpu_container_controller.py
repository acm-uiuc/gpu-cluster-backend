from ..database import db_session
from ..models import Instance
from .container_controller import ContainerController
from nvdocker import NVDockerClient


class GPUContainerController(ContainerController):

    def __init__(self, config):
        super().__init__(config)
        self.docker_client = NVDockerClient()

    def create_container(self, image, user="", token_required=False, budget=-1, num_gpus=1):
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

        # create container
        container_list = self.docker_client.docker_image_list(filters={'name': image})
        print(image)
        if container_list:
            c_id = self.docker_client.create_container(image, **container_config).id

        else:
            # Add a client.images.search to check if the path to the container exists on docker hub. If not, error out
            has_result = self.docker_client.docker_image_search(image)
            if not has_result:
                print('No image in DockerHub')
                return 'No image in DockerHub' , '', ''

            image_tag = image.split(':')
            docker_image = self.docker_client.docker_image_pull(image_tag[0], image_tag[1])

            # If pull returns more than one image, get the first one in the list
            if hasattr(docker_image, '__len__'):
                docker_image = docker_image[0]
            print(docker_image)

            # Do you have to build the image after you pull it from Docker Hub?
            c_id = self.docker_client.create_container(docker_image, **container_config).id

        # assemble endpoints for UI, monitor and get the access token if needed
        uurl = ""
        murl = ""
        token = ""
        if token_required:
            token = self.docker_client.exec_run(c_id, 'python3 /opt/cluster-container/jupyter_get.py')
            uurl = "http://vault.acm.illinois.edu:{}/?token={}".format(uport, token.decode("utf-8"))
            murl = "http://vault.acm.illinois.edu:" + str(mport)
        else:
            uurl = "http://vault.acm.illinois.edu:" + str(uport)
            murl = "http://vault.acm.illinois.edu:" + str(mport)

        # TODO insert budget
        budget = -1
        db_session.add(Instance(c_id, uport, mport, uurl, murl, user, budget, token))
        db_session.commit()
        return c_id, uurl, murl

    def kill_container(self, c_id):
        self.docker_client.stop_container(c_id)
