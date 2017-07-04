__author__ = 'ffuuugor'
import cherrypy
from models import Game, Point, Task, as_dict
from datetime import datetime, timedelta
from utils import get_session_info
from sqlalchemy import or_
from LatLon import LatLon, Longitude, Latitude, GeoVector
import random
CRIME_EXPOSURE_TIME = timedelta(minutes=2)

class Api(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def game_status(self):
        game, tasks = get_session_info()

        if game:
            return {"game_status": game.status}
        else:
            return {"game_status": "no_games"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def solved_cnt(self):
        game, tasks = get_session_info()
        val = 0
        for task, point in tasks:
            if task.status == "solved":
                val += 1
        return {"val":val}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def start_game(self):
        try:
            game, tasks = get_session_info()
            if game.status == "new":
                game.status = "active"
                cherrypy.request.db.add(game)
                cherrypy.request.db.commit()
                return {"status": "success"}
            else:
                return {"status": "fail", "msg": "Wrong game status %s. Should be new" % game.status}
        except Exception:
            cherrypy.request.db.rollback()
            raise

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def make_newgame(self):
        try:
            old_games = cherrypy.request.db.query(Game) \
                .filter(or_(Game.status == "active", Game.status == "new"))\
                .all()

            for old_game in old_games:
                old_game.status = "closed"
                cherrypy.request.db.add(old_game)

            game = Game(status="new", created=datetime.now())
            cherrypy.request.db.add(game)

            #create tasks
            photo_points = cherrypy.request.db.query(Point).all()
            for point in photo_points:

                real_center = LatLon(Latitude(point.lat), Longitude(point.lng))
                offset = GeoVector(initial_heading=random.randint(0,360),
                                   distance=random.randint(0,point.radius)/1000.0)

                task_center = real_center + offset

                task = Task(
                    game_id=game.id,
                    point_id=point.id,
                    center_lat=task_center.lat.decimal_degree,
                    center_lng=task_center.lon.decimal_degree,
                    status="available"
                )

                cherrypy.request.db.add(task)

            cherrypy.request.db.commit()
            return {"status": "success"}
        except Exception:
            cherrypy.request.db.rollback()
            raise



