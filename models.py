from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from db_connector import Base

class Instance(Base):
    __tablename__ = 'InstanceAssignments'
    id = Column(Integer, primary_key=True)
    ui_port = Column(Integer)
    monitor_port = Column(Integer)
    ui_link = Column(String(100))
    monitory_link = Column(String(100))
    user = Column(String(10))
    budget = Column(Integer)
    start_time = Column(DateTime, default=datetime.utcnow)
    
    def __init__(self, uiport, mport, ui_link, monitor_link, user, budget):
        self.ui_port = uiport
        self.monitor_port = mport
        self.ui_link = ui_link
        self.monitory_link = monitor_link
        self.user = user
        self.budget = budget

    def __repr__(self):
        return '<Instance %r>' % (self.user)