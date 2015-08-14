__author__ = 'ffuuugor'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, Integer, Float, Enum, DateTime, Boolean
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'u'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String, primary_key=True)
    password = Column("password", String)
    phone = Column("phone", String)

class Game(Base):
    __tablename__ = 'game'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)

class Task(Base):
    __tablename__ = 'task'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    game_id = Column("game_id", Integer, ForeignKey("mrx.game.id"))
    point_id = Column("point_id", Integer, ForeignKey("mrx.photo_point.id"))
    center_lat = Column("center_lat", Float)
    center_lng = Column("center_lng", Float)
    radius = Column("radius", Float)
    status = Column("status", Enum("open","done","closed", name="task_status"))

    point = relationship("Point", backref="photo_point")

class Point(Base):
    __tablename__ = 'photo_point'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    lat = Column("lat", Float)
    lng = Column("lng", Float)
    img_uri = Column("img_uri", String)
    answer = Column("answer", ARRAY(String))

class MrXPos(Base):
    __tablename__ = 'mrx_pos'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    lat = Column("lat", Float)
    lng = Column("lng", Float)
    time = Column("time", DateTime)
    exposed = Column("exposed", Boolean)

    game_id = Column("game_id", Integer, ForeignKey("mrx.game.id"))



def as_dict(model, columns=None):

    if hasattr(model,"__table__"):
        ret = {c.name: getattr(model, c.name) for c in model.__table__.columns}
    else:
        ret = {}
        for one in model:
            ret.update({c.name: getattr(one, c.name) for c in one.__table__.columns})

    if columns is not None:
        ret = {x: ret.get(x) for x in columns}

    for key in ret.keys():
        if type(ret[key]) == datetime:
            ret[key] = str(ret[key])

    return ret

