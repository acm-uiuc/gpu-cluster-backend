#Just testing the docker-py SDK
import docker

class CWDockerClient:
    client = None

    gpu_devices = ['/dev/nvidiactl', '/dev/nvidia-uvm',
                   '/dev/nvidia3', '/dev/nvidia2', '/dev/nvidia1', '/dev/nvidia0']
    nvidia_driver = 'nvidia-docker'
    nvidia_volume = ['nvidia_driver_387.12:/usr/local/nvidia:ro']
    
    def __init__(self):
        self.client = docker.from_env(version='auto')
        
    def create_container(self, cmd, image=None, is_gpu = False):
        if(image is None):
            c = self.client.containers.run('registry.gitlab.com/acm-uiuc/sigops/clearwaters-docker/ubuntu-mpich-arm64', cmd, detach=True)
        else:
            if(is_gpu):
                c = self.client.containers.run(image, cmd, devices=self.gpu_devices, volume_driver=self.nvidia_driver, volumes=self.nvidia_volume, detach=True)
            else:
                c = self.client.containers.run(image, cmd, detach=True)
            
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
        print(c.exec_run(cmd))
    
