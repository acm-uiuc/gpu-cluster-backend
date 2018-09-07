import abc
import time
import random
from celery import Celery
from celery.schedules import crontab
from ..database import db_session
from ..models import Instance

class ContainerController(abc.ABC):
    '''
    __init__(self, config): creates a Container Supervisor (either CPU-Only or GPU)
    Args: config - Application config dict requires a field for the price_per_hour
    '''
    def __init__(self, config):
        super().__init__()
        self.hourly_rate = config["price_per_hour"]

    '''
    CONTAINER CONTROLLER
    '''
    @abc.abstractmethod
    def create_container(self, image, user="", token_required=False, budget=-1):
        pass 

    @abc.abstractmethod
    def kill_container(self, c_id):
        pass

    def launch_container(self, c_id):
        container_instance = db_session.query(Instance).filter_by(cid = c_id).first()
        container_exists = True if container_instance != None else False
        if container_exists:
            container_instance.launched = True
            db_session.commit()
        return container_exists

    '''
    STATUS QUERIERS
    '''

    def verify_launch(self, c_id):
        instance = db_session.query(Instance).filter_by(cid = c_id).first() 
        return True if instance.launched == True else False
        
    def verify_underbudget(self, c_id):
        instance = db_session.query(Instance).filter_by(cid = c_id).first() 
        return True if self.balence(instance) <= instance.budget else False 

    '''
    UTILITES
    '''

    '''
    balance(c_id): calculates the ammount of credits spent so far 
    Args: c_id: container ID
    '''
    def balance(container):
        if type(container) is str:
            container_instance = db_session.query(Instance).filter_by(cid = c_id).first()
            return self.hourly_rate * (60 * 60 * (time.time() - container_instance.start_time)) 
        elif type(container) is Instance:
            return self.hourly_rate * (60 * 60 * (time.time() - container.start_time)) 

    def get_port(self):
        while True:
            rand_port = random.randint(80, 65535)
            used_jports = db_session.query(Instance).filter_by(ui_port = rand_port).first()
            used_mports = db_session.query(Instance).filter_by(monitor_port = rand_port).first()
            if (used_jports == None) and (used_mports == None):
                return rand_port

