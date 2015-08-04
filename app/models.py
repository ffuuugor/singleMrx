__author__ = 'ffuuugor'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, Integer, Float, Enum
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

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
    status = Column("status", Enum("open","done","closed"))

class Point(Base):
    __tablename__ = 'photo_point'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    lat = Column("lat", Float)
    lng = Column("lng", Float)
    img_uri = Column("img_uri", String)

class Answer(Base):
    __tablename__ = 'photo_answer'
    __table_args__ = {'schema': 'mrx'}

    id = Column("id", Integer, ForeignKey("mrx.photo_point.id"), primary_key=True)
    answer = Column("answer", ARRAY(String))

def as_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}
