__author__ = 'ffuuugor'
import cherrypy
from models import Game, User, Role, Point, Crime, Task, as_dict
from auth import SESSION_KEY, require
from datetime import datetime, timedelta
from utils import get_session_info
from sqlalchemy import or_

CRIME_EXPOSURE_TIME = timedelta(minutes=2)
START_HANDICAP = 0

class TaskApi(object):

    def make_one_task(self, crime, task, point):
        one = {"id":crime.id,
                "lat":crime.center_lat,
                "lng":crime.center_lng,
                "radius":crime.radius,
                "status":crime.status
                }

        if task.status == "requested":
            if task.request_time + task.walk_time > datetime.now():
                one["remaining"] = (task.request_time + task.walk_time - datetime.now()).seconds
            else:
                task.status = "active"
                cherrypy.request.db.add(task)
                cherrypy.request.db.commit()

        if task.status == "active":
            if point.img_uri.startswith("http://") or point.img_uri.startswith("https://"):
                one["img_url"] = point.img_uri
            else:
                one["img_url"] = "static/image/uploads/%s" % point.img_uri

        one["task_status"] = task.status

        return one


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def list(self):
        user, role, game, all_tasks = get_session_info()

        ret = []
        if role.role == "mrx":
            for task, crime, point in all_tasks:
                ret.append(self.make_one_task(crime,task,point))

        elif role.role == "detective":
            #manage start handicap
            commited_cnt = cherrypy.request.db.query(Crime).filter(Crime.game_id == game.id)\
                .filter(or_(Crime.status == "commited", Crime.status == "solved")).count()

            if commited_cnt > START_HANDICAP:
                for task, crime, point in all_tasks:
                    if crime.status not in ("commited", "solved"):
                        continue

                    if crime.status == "commited" and \
                        crime.commit_time + CRIME_EXPOSURE_TIME > datetime.now():
                        continue

                    ret.append(self.make_one_task(crime,task,point))

        cherrypy.request.db.commit()
        return ret

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    @cherrypy.tools.allow(methods=['POST'])
    def take(self, id):
        try:
            user, role, game, all_tasks = get_session_info()

            active_tasks = filter(lambda x: x[0].status == "active" or x[0].status == "requested", all_tasks)
            if len(active_tasks) > 0:
                return {"status":"fail","msg":"Only one task can be active at a time"}

            task, crime, point = filter(lambda x: x[1].id == int(id), all_tasks)[0]

            if task.status != "pending":
                return {"status":"fail", "msg":"Wrong task status %s. Should be pending" % task.status}

            task.status = "requested"
            task.request_time = datetime.now()

            time_to_walk = timedelta(minutes=1) #TODO actually calculate
            task.walk_time = time_to_walk

            cherrypy.request.db.add(task)
            cherrypy.request.db.commit()
            return {"status":"success", "remaining": time_to_walk.seconds}
        except:
            cherrypy.request.db.rollback()
            raise

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    @cherrypy.tools.allow(methods=['POST'])
    def cancel(self, id):
        user, role, game, all_tasks = get_session_info()

        task, crime, point = filter(lambda x: x[1].id == int(id), all_tasks)[0]

        if task.status not in ("requested","active"):
            return {"status":"fail", "msg":"Wrong task status %s. Should be active" % task.status}

        task.status = "cancelled"
        cherrypy.request.db.add(task)
        cherrypy.request.db.commit()
        return {"status":"success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    @cherrypy.tools.allow(methods=['POST'])
    def answer(self, id, answer):
        user, role, game, all_tasks = get_session_info()
        task, crime, point = filter(lambda x: x[1].id == int(id), all_tasks)[0]

        if task.status not in ("active"):
            return {"status":"fail", "msg":"Wrong task status %s. Should be active" % task.status}

        if answer in point.answer:
            task.status = "completed"
            if role.role == "mrx":
                crime.status = "commited"
                crime.commit_time = datetime.now()

                det_task = cherrypy.request.db.query(Task)\
                            .join(Crime, Crime.det_task_id == Task.id)\
                            .filter(Crime.id == crime.id).one()

                det_task.status = "pending"
                cherrypy.request.db.add(task)
            else:
                crime.status = "solved"

            cherrypy.request.db.add(task)
            cherrypy.request.db.add(crime)
            cherrypy.request.db.commit()

            return {"status":"success"}
        else:
            return {"status":"fail", "msg":"Wrong answer"}
