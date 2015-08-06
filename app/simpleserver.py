__author__ = 'ffuuugor'
import cherrypy
import os
import sys
from models import Game, Task, Point, MrXPos, as_dict
import json
import datetime

PATH = os.path.abspath(os.path.dirname(__file__))
class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        l = len(cherrypy.request.db.query(Game).all())
        return "Hello world! %d" % l

    @cherrypy.expose
    @cherrypy.tools.json_out()
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
                    return {"status":"correct"}
                else:
                    return {"status":"wrong"}

        else:
            raise cherrypy.HTTPError(400)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.allow(methods=['POST'])
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
    def get_exposed_pos(self):
        positions = cherrypy.request.db.query(MrXPos).filter(MrXPos.exposed == True).all()
        return [as_dict(x) for x in positions]


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
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







