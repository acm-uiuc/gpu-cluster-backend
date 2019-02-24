from celery import Celery
from celery.schedules import crontab
from ..database import db_session
from ..models import Instance
from .container_controller import ContainerController
import docker


class CPUContainerController(ContainerController):

    def __init__(self, config):
        super().__init__(config)
        self.client = docker.from_env(version='auto')

    def create_container(self, image, user="", token_required=False, budget=-1):
        uport = self.get_port()
        mport = self.get_port()
        while uport == mport:
            mport = self.get_port()

        ports = {'8888/tcp': uport,
                 '6006/tcp': mport}

        print(image)
        container_list = self.client.containers.list(filters={'name': image})
        print(image + "test")

        if container_list:
            c_id = self.client.containers.run(image, "", auto_remove=True, detach=True, ports=ports).id

        else:
            # Add a client.images.search to check if the path to the container exists on docker hub. If not, error out
            # docker_result = self.client.images.search(image)
            # print(docker_result)
            image_tag = image.split(':')
            docker_image = self.client.images.pull('illiyan/test_container', 'latest')

            # If pull returns more than one image, get the first one in the list
            if hasattr(docker_image, '__len__'):
                docker_image = docker_image[0]

            # Do you have to build the image after you pull it from Docker Hub?
            c_id = self.client.containers.run(docker_image, '', auto_remove=True, detach=True, ports=ports).id
        print(c_id)

        uurl = ""
        murl = ""
        if token_required:
            c = self.client.containers.get(c_id)
            token = c.exec_run('python3 /opt/cluster-container/jupyter_get.py')
            uurl = "http://localhost:{}/?token={}".format(uport, token.decode("utf-8"))
            murl = "http://localhost:" + str(mport)
        else:
            uurl = "http://localhost:" + str(uport)
            murl = "http://localhost:" + str(mport)
        print(image)
        # TODO insert budget
        db_session.add(Instance(c_id, uport, mport, uurl, murl, user, budget, token))
        db_session.commit()
        return c_id, uurl, murl

    def kill_container(self, c_id):
        c = self.client.containers.get(c_id)
        c.stop()
