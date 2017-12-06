from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Ports(db.Model):
    __tablename__ = 'docker_ports'
    id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer)
    link = db.Column(db.String(100))
    
    def __init__(self, port, link):
        self.port = port
        self.link = link

