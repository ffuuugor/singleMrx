__author__ = 'ffuuugor'
import cherrypy
import os
import sys
from models import Game, Task, as_dict
import json

PATH = os.path.abspath(os.path.dirname(__file__))
class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        l = len(cherrypy.request.db.query(Game).all())
        return "Hello world! %d" % l

    @cherrypy.expose
    def task(self):
        ret = map(as_dict, cherrypy.request.db.query(Task).all())
        return json.dumps(ret)
