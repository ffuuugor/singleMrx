__author__ = 'ffuuugor'
import cherrypy
import os
import sys
from models import Game, Task, Point, MrXPos, as_dict
import json
import datetime
import cgi
import tempfile
import mimetypes
import hashlib
import time
from auth import AuthController, require, SESSION_KEY
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('view'))
mimetypes.init()

class HelloWorld(object):

    @cherrypy.expose
    @require()
    def index(self):
        tmpl = env.get_template('index.html')
        return tmpl.render()

    @cherrypy.expose
    @require()
    def admin(self):
        tmpl = env.get_template('admin.html')
        return tmpl.render()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def task(self, id=None):
        query = cherrypy.request.db.query(Task, Point).join(Point)
        if id is not None:
            query = query.filter(Task.id == id)

        columns = ["id", "point_id", "status","center_lat",
                   "center_lng", "radius", "img_uri"]

        ret = [as_dict(x, columns) for x in query.all()]
        return ret

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.allow(methods=['POST'])
    @require()
    def answer(self, task_id):
        input_json = cherrypy.request.json

        if "answer" in input_json:
            user_answer = input_json["answer"]
            db_result = cherrypy.request.db.query(Task, Point).join(Point).filter(Task.id == task_id).all()

            if len(db_result) > 1:
                raise Exception("Several points for one id %s" % str(task_id))
            else:
                task = db_result[0][0]
                point = db_result[0][1]

                correct_answers = [x.lower() for x in point.answer]

                if user_answer.lower() in correct_answers:
                    task.status = "done"
                    cherrypy.request.db.commit()
                    return {"status":"success"}
                else:
                    return {"status":"wrong"}

        else:
            raise cherrypy.HTTPError(400)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.allow(methods=['POST'])
    @require()
    def add_mrx_pos(self):
        input_json = cherrypy.request.json

        if "lat" in input_json and "lng" in input_json:
            mrx_pos = MrXPos(lat=input_json["lat"], lng=input_json["lng"],
                             time=datetime.datetime.now(), exposed=False, game_id=1)

            cherrypy.request.db.add(mrx_pos)
            cherrypy.request.db.commit()

            return {"status":"success"}
        else:
            raise cherrypy.HTTPError(400)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def get_exposed_pos(self):
        positions = cherrypy.request.db.query(MrXPos).filter(MrXPos.exposed == True).all()
        return [as_dict(x) for x in positions]


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    @require()
    def use_task(self, task_id):
        task = cherrypy.request.db.query(Task).filter(Task.id == task_id).first()

        if task.status != "done":
            return {"status":"wrong task status"}

        mrx_pos = cherrypy.request.db.query(MrXPos).order_by(MrXPos.time.desc()).first()

        if mrx_pos.exposed:
            return {"status":"already exposed"}
        else:
            mrx_pos.exposed = True
            task.status = "closed"
            cherrypy.request.db.commit()
            return {"status":"success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def upload(self, file, lat, lng, answer):
        extension = mimetypes.guess_extension(file.content_type.value)
        filename = hashlib.md5(str(time.time())).hexdigest() + extension
        filepath = os.path.join(cherrypy.config["mrx.uploads.dir"], filename)

        f = open(filepath,"w")
        data = file.file.read()
        print >> f, data
        f.close()

        point = Point(lat=float(lat), lng=float(lng), answer=answer.split(','), img_uri=filename)
        cherrypy.request.db.add(point)
        cherrypy.request.db.commit()









