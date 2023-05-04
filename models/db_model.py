from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from typing import Type

db = SQLAlchemy()

class Server(db.Model):
    id: Type[Column] = db.Column(Integer, primary_key=True, nullable=False)
    servername: Type[Column] = db.Column(String(256), unique=False, nullable=False)
    exec_cmd: Type[Column] = db.Column(String(2048), unique=False, nullable=False)
    cwd: Type[Column] = db.Column(String(2048), unique=False, nullable=False)

    def to_dict(self, is_alive: bool):
        return {
            "id": self.id,
            "servername": self.servername,
            "exec_cmd": self.exec_cmd,
            "cwd": self.cwd,
            "is_alive": is_alive,
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
