from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from .. database import Base

class Instance(Base):
    __tablename__ = 'Instance'
    id =            Column(Integer, primary_key=True)
    cid =           Column(Integer)
    ui_port =       Column(Integer)
    monitor_port =  Column(Integer)
    ui_link =       Column(String(100))
    monitory_link = Column(String(100))
    user =          Column(String(10))
    budget =        Column(Integer)
    start_time =    Column(DateTime, default=datetime.utcnow)
    launched =      Column(Boolean)
    token =         Column(String, nullable=True)
    
    def __init__(self, cid,  uiport, mport, ui_link, monitor_link, user, budget, start_time, token):
        self.cid =  cid
        self.ui_port = uiport
        self.monitor_port = mport
        self.ui_link = ui_link
        self.monitory_link = monitor_link
        self.user = user
        self.budget = budget
        self.start_time = start_time
        self.launched = False
        self.token = token

    def __repr__(self):
        return '<Instance %r>' % (self.user)


