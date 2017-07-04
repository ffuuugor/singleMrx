__author__ = 'ffuuugor'
import cherrypy
import os
import sys
from models import Game, Task, Point, as_dict
import json
import datetime
import cgi
import tempfile
import mimetypes
import hashlib
import time
from jinja2 import Environment, FileSystemLoader
from utils import get_session_info

env = Environment(loader=FileSystemLoader('view'))
mimetypes.init()

class View(object):

    @cherrypy.expose
    def index(self):
        game, all_tasks = get_session_info()

        if game is None:
            return "No active or scheduled games"

        if game.status == "active":
            tmpl = env.get_template('newindex.html')
        elif game.status == "new":
            tmpl = env.get_template('startpage.html')
        else:
            tmpl = env.get_template('gameover.html')

        return tmpl.render()

    @cherrypy.expose
    def admin(self):
        tmpl = env.get_template('admin.html')
        return tmpl.render()


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload(self, file, lat, lng, answer, question, comment, radius, has_present=False):
        extension = mimetypes.guess_extension(file.content_type.value)
        filename = hashlib.md5(str(time.time())).hexdigest() + extension
        filepath = os.path.join(cherrypy.config["mrx.uploads.dir"], filename)

        f = open(filepath,"w")
        data = file.file.read()
        print >> f, data
        f.close()

        point = Point(lat=float(lat), lng=float(lng), answer=answer.split(','),
                      img_uri=filename, question=question, comment=comment, radius=int(radius), has_present=has_present)
        cherrypy.request.db.add(point)
        cherrypy.request.db.commit()