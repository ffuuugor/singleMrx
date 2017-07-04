__author__ = 'ffuuugor'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, Integer, Float, Enum, DateTime, Boolean, Time, Interval
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()

class Game(Base):
    __tablename__ = 'game'
    __table_args__ = {'schema': 'smrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", Enum("new", "active","finished","closed", name="game_status", schema="smrx"))
    created = Column("created", DateTime)
    start = Column("start", DateTime)
    finish = Column("duration", DateTime)


class Task(Base):
    __tablename__ = 'task'
    __table_args__ = {'schema': 'smrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    game_id = Column("game_id", Integer, ForeignKey("smrx.game.id"))
    point_id = Column("point_id", Integer, ForeignKey("smrx.photo_point.id"))
    center_lat = Column("center_lat", Float)
    center_lng = Column("center_lng", Float)
    status = Column("status", Enum("available","active","solved", name="task_status", schema="smrx"))

    point = relationship("Point")


class Point(Base):
    __tablename__ = 'photo_point'
    __table_args__ = {'schema': 'smrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    lat = Column("lat", Float)
    lng = Column("lng", Float)
    radius = Column("radius", Float)
    img_uri = Column("img_uri", String)
    question = Column("question", String)
    answer = Column("answer", ARRAY(String))
    comment = Column("comment", String)
    has_present = Column("has_present", Boolean)




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

