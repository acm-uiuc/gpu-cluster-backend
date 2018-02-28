import os
import random
import time
import abc
from ..database import db_session
from ..models import Instance

class Cluster(abc.ABC):
    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def create_container(self):
        pass

    @abc.abstractmethod
    def confirm_launch(self):
        pass
    
    @staticmethod
    def get_port():
        while True:
            rand_port = random.randint(80, 65535)
            used_jports = db_session.query(Instance).filter_by(ui_port = rand_port).first()
            used_mports = db_session.query(Instance).filter_by(monitor_port = rand_port).first()
            if (used_jports == None) and (used_mports == None):
                return rand_port

    def register_routes(self, app):
        app.add_url_rule('/create_container', 'create_container', self.create_container, methods=['POST'])
        app.add_url_rule('/confirm',          'confirm',          self.confirm_launch,   methods=['POST'])