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

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
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
            return {"status":"missing answer"}




