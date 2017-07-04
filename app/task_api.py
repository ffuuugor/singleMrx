__author__ = 'ffuuugor'
import cherrypy
from models import Game, Point, Task, as_dict
from datetime import datetime, timedelta
from utils import get_session_info
from sqlalchemy import or_
from geopy.distance import vincenty
import logging

CRIME_EXPOSURE_TIME = timedelta(minutes=2)
START_HANDICAP = 2

class TaskApi(object):

    @staticmethod
    def _make_url(uri):
        if uri.startswith("http://") or uri.startswith("https://"):
            return uri
        else:
            return "static/image/uploads/%s" % uri

    def make_one_task(self, task, point):
        one = {"id":task.id,
                "lat":task.center_lat,
                "lng":task.center_lng,
                "radius":point.radius,
                "status":task.status
               }

        if task.status == "active":
            one["img_url"] = self._make_url(point.img_uri)
            one["text"] = point.question

        return one


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def list(self):
        game, all_tasks = get_session_info()

        ret = []
        for task, point in all_tasks:
            ret.append(self.make_one_task(task,point))

        return ret


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def take(self, id):
        try:
            game, all_tasks = get_session_info()

            active_tasks = filter(lambda x: x[0].status == "active", all_tasks)
            if len(active_tasks) > 0:
                return {"status":"fail","msg":"Only one task can be active at a time"}

            task, point = filter(lambda x: x[0].id == int(id), all_tasks)[0]

            if task.status != "available":
                return {"status":"fail", "msg":"Wrong task status %s. Should be pending" % task.status}

            task.status = "active"

            cherrypy.request.db.add(task)
            cherrypy.request.db.commit()
            return {"status":"success"}
        except:
            cherrypy.request.db.rollback()
            raise

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def pause(self, id):
        game, all_tasks = get_session_info()

        task, point = filter(lambda x: x[0].id == int(id), all_tasks)[0]

        if task.status != "active":
            return {"status":"fail", "msg":"Wrong task status %s. Should be active" % task.status}

        task.status = "available"
        cherrypy.request.db.add(task)
        cherrypy.request.db.commit()
        return {"status":"success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def answer(self, id, answer):
        game, all_tasks = get_session_info()

        task, point = filter(lambda x: x[0].id == int(id), all_tasks)[0]

        if task.status != "active":
            return {"status":"fail", "msg":"Wrong task status %s. Should be active" % task.status}

        correct_answers = map(lambda x: x.lower().strip(), point.answer)
        if answer.lower().strip() in correct_answers:
            task.status = "solved"

            if all([task.status == "solved" for task, point in all_tasks]):
                game.status = "finished"

            cherrypy.request.db.add(task)
            cherrypy.request.db.add(game)
            cherrypy.request.db.commit()

            return {"status":"success"}
        else:
            return {"status":"fail", "msg":"Wrong answer"}
