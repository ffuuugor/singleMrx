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
        query = cherrypy.request.db.query(Task, Point).join(Point)
        if id is not None:
            query = query.filter(Task.id == id)

        columns = ["id", "point_id", "status","center_lat","center_lng", "radius", "img_uri"]

        ret = [as_dict(x, columns) for x in query.all()]
        return json.dumps(ret)


