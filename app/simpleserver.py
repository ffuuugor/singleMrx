__author__ = 'ffuuugor'
import cherrypy
import os
import sys
from models import Game, Task, Point, as_dict
import json

PATH = os.path.abspath(os.path.dirname(__file__))
class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        l = len(cherrypy.request.db.query(Game).all())
        return "Hello world! %d" % l

    @cherrypy.expose
    def task(self, id=None):
        query = cherrypy.request.db.query(Task)
        if id is not None:
            query = query.filter(Task.id == id)

        ret = map(as_dict, query.all())
        return json.dumps(ret)

    @cherrypy.expose
    def point(self, id=None):
        query = cherrypy.request.db.query(Point)
        if id is not None:
            query = query.filter(Point.id == id)

        ret = map(as_dict, query.all())
        return json.dumps(ret)
