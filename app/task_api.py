__author__ = 'ffuuugor'
import cherrypy
from models import Game, User, Role, Point, Crime, Task, as_dict
from auth import SESSION_KEY, require
from datetime import datetime, timedelta
from utils import get_session_info
from sqlalchemy import or_
from geopy.distance import vincenty

CRIME_EXPOSURE_TIME = timedelta(minutes=2)
START_HANDICAP = 2

class TaskApi(object):

    def calculateTimeToWalk(self, prevCrime, newCrime):
        if prevCrime is None:
            return 600

        from_point = (prevCrime.center_lat, prevCrime.center_lng)
        to_point = (newCrime.center_lat, newCrime.center_lng)

        meters = vincenty(from_point, to_point).meters

        # expected speed: 1 m/s
        if meters < 60:
            return 60
        else:
            return int(meters)


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

            one["text"] = point.text;

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
            if game.status == "active":
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

            prev_crimes = filter(lambda x: x[0].status in ("cancelled", "completed"), all_tasks)
            if len(prev_crimes) == 0:
                prev_crime = None
            else:
                prev_crime =sorted(prev_crimes, key = lambda x: x[0].request_time)[-1][1]

            seconds_to_walk = self.calculateTimeToWalk(prev_crime, crime) #TODO actually calculate
            task.walk_time = timedelta(seconds=seconds_to_walk)

            cherrypy.request.db.add(task)
            cherrypy.request.db.commit()
            return {"status":"success", "remaining": seconds_to_walk}
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

        correct_answers = map(lambda x: x.lower(), point.answer)
        if answer.lower() in correct_answers:
            task.status = "completed"
            if role.role == "mrx":
                crime.status = "commited"
                crime.commit_time = datetime.now()

                det_task = cherrypy.request.db.query(Task)\
                            .join(Crime, Crime.det_task_id == Task.id)\
                            .filter(Crime.id == crime.id).one()

                det_task.status = "pending"
                cherrypy.request.db.add(det_task)

                commited_cnt = cherrypy.request.db.query(Crime).filter(Crime.game_id == game.id)\
                    .filter(or_(Crime.status == "commited", Crime.status == "solved")).count()

                if game.status == "mrx_active" and commited_cnt >= START_HANDICAP:
                    game.status = "active"
                    game.detective_start = datetime.now()

            else:
                crime.status = "solved"

            cherrypy.request.db.add(task)
            cherrypy.request.db.add(crime)
            cherrypy.request.db.add(game)
            cherrypy.request.db.commit()

            return {"status":"success"}
        else:
            return {"status":"fail", "msg":"Wrong answer"}
