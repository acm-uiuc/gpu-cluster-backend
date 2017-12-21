from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class InstanceAssigment(Base):
    __tablename__ = 'InstanceAssignments'
    id = Column(Integer, primary_key=True)
    jupyter_port = Column(Integer)
    monitor_port = Column(Integer)
    jupyter_link = Column(String(100))
    monitory_link = Column(String(100))
    user = Column(String(10))
    
    def __init__(self, jport, mport, jupyter_link, monitor_link, user):
        self.jupyter_port = jport
        self.monitor_port = mport
        self.jupyter_link = jupyter_link
        self.monitory_link = monitor_link
        self.user = user

    def __repr__(self):
        return '<Assignment %r>' % (self.user)