import abc
import time
import random
from celery import Celery
from celery.schedules import crontab
from ..database import db_session
from ..models import Instance

class Supervisor(abc.ABC):

    balance = lambda self: self.exchange_rate * (60 * 60 * (time.time() - start)) 

    def __init__(self, config):
        super().__init__()
        self.exchange_rate = config["price_per_hour"]

    @abc.abstractmethod
    def create_container(self, image, user="", token_required=False, budget=-1):
        pass 

    @abc.abstractmethod
    def kill_container(self, c_id):
        pass

    def verify_launch(self, c_id):
        return True if db_session.query(Instance).filter_by(cid = c_id).first() != None else False
        

    def verify_budget(self, c_id):
        instance = db_session.query(Instance).filter_by(cid = c_id).first() 
        if balance >= instance.budget:
            self.kill_container(c_id)
            return

    def get_port(self):
        while True:
            rand_port = random.randint(80, 65535)
            used_jports = db_session.query(Instance).filter_by(ui_port = rand_port).first()
            used_mports = db_session.query(Instance).filter_by(monitor_port = rand_port).first()
            if (used_jports == None) and (used_mports == None):
                return rand_port

