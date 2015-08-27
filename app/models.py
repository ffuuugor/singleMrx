__author__ = 'ffuuugor'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, Integer, Float, Enum, DateTime, Boolean, Time, Interval
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'u'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String, unique=True)
    password = Column("password", String)
    phone = Column("phone", String)

class Token(Base):
    __tablename__ = 'token'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("mrx.u.id"))
    token = Column("tokne", String)

    user = relationship(User, backref="tokens")

class Game(Base):
    __tablename__ = 'game'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", Enum("new", "mrx_active", "active","finished", name="game_status", schema="mrx"))
    start = Column("start", DateTime)
    detective_start = Column("detective_start", DateTime)
    duration = Column("duration", Interval)
    code = Column("code", String)

class Role(Base):
    __tablename__ = 'role'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("mrx.u.id"))
    game_id = Column("gamr_id", Integer, ForeignKey("mrx.game.id"))
    role = Column("role", Enum("detective","mrx", name="game_role", schema="mrx"))

    game = relationship(Game, backref="roles")
    user = relationship(User, backref="roles")

class Location(Base):
    __tablename__ = 'location'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("mrx.u.id"))
    game_id = Column("game_id", Integer, ForeignKey("mrx.game.id"))
    lat = Column("lat", Float)
    lng = Column("lng", Float)
    time = Column("time", DateTime)

    game = relationship(Game)

class Task(Base):
    __tablename__ = 'task'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    game_id = Column("game_id", Integer, ForeignKey("mrx.game.id"))
    status = Column("status", Enum("unavailable", "pending", "requested",
                                   "active", "cancelled", "completed", name="task_status", schema="mrx"))
    request_time = Column("request_time", DateTime)
    walk_time = Column("walk_time", Interval)

    game = relationship("Game")

class Crime(Base):
    __tablename__ = 'crime'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    game_id = Column("game_id", Integer, ForeignKey("mrx.game.id"))
    point_id = Column("point_id", Integer, ForeignKey("mrx.photo_point.id"))
    center_lat = Column("center_lat", Float)
    center_lng = Column("center_lng", Float)
    radius = Column("radius", Float)
    status = Column("status", Enum("not_commited","commited","solved", name="crime_status", schema="mrx"))
    commit_time = Column("commit_time", DateTime)

    mrx_task_id = Column("mrx_task_id", Integer, ForeignKey("mrx.task.id"))
    det_task_id = Column('det_task_id', Integer, ForeignKey("mrx.task.id"))

    point = relationship("Point")
    mrx_task = relationship("Task", foreign_keys=mrx_task_id)
    det_task = relationship("Task", foreign_keys=det_task_id)

class Point(Base):
    __tablename__ = 'photo_point'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    lat = Column("lat", Float)
    lng = Column("lng", Float)
    radius = Column("radius", Float)
    img_uri = Column("img_uri", String)
    answer = Column("answer", ARRAY(String))

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

