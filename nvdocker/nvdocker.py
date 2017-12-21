#Just testing the docker-py SDK
import docker

class NVDockerClient:
    client = None

    gpu_devices = ['/dev/nvidiactl', '/dev/nvidia-uvm', '/dev/nvidia1', '/dev/nvidia0']
    nvidia_driver = 'nvidia-docker'
    volumes = {'nvidia_driver_387.12':{'bind':'/usr/local/nvidia', 'mode':'ro'},
               '/vault':              {'bind':'/vault', 'mode':'rw'}}
    ports = {'8888/tcp':8890,
             '6006/tcp':6969}
    
    def __init__(self):
        self.client = docker.from_env(version='auto')
        
    def create_container(self, cmd, image=None, is_gpu=False, ports=None, user=""):
        home_dir = "/vault/"
        if user != "":
            home_dir = home_dir + user

        if ports is not None:
            self.ports['8888/tcp'] = ports[0]
            self.ports['6006/tcp'] = ports[1]

        if is_gpu:
            c = self.client.containers.run(image, cmd, auto_remove=True, ports=self.ports, devices=self.gpu_devices, volume_driver=self.nvidia_driver, volumes=self.volumes, detach=True, working_dir=home_dir)
        else:
            c = self.client.containers.run(image, cmd, auto_remove=True, detach=True, working_dir=home_dir)
            
        return c.id

    def build_image(self, path):
        img = self.client.images.build(path);
        return img
        
    def get_container_logs(self, cid):
        c = self.client.containers.get(cid)
        return c.logs()

    def get_all_container_ids(self):
        return self.client.containers.list()
    
    def stop_container(self, cid):
        c = self.client.containers.get(cid)
        c.stop()

    def start_container(self, cid):
        c = self.client.containers.get(cid)
        c.start()
    
    def start_all_containers(self):
        for c in self.client.containers.list():
            c.start()
        
    def stop_all_containers(self):    
        for c in self.client.containers.list():
            c.stop()

    def run_cmd(self, cid, cmd):
        c = self.client.containers.get(cid)
        return c.exec_run(cmd)
    
