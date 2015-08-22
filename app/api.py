__author__ = 'ffuuugor'
import cherrypy
from models import Game, User, Role, Point, Crime, Task, Location, as_dict
from auth import SESSION_KEY, require
from datetime import datetime, timedelta
from utils import get_session_info
from sqlalchemy import or_

CRIME_EXPOSURE_TIME = timedelta(minutes=2)

class Api(object):

    def get_delta(self, game_id):
        cnt = cherrypy.request.db.query(Crime).filter(Crime.game_id == game_id)\
            .filter(Crime.status == "commited").count()

        return cnt

    def get_solved(self, game_id):
        cnt = cherrypy.request.db.query(Crime).filter(Crime.game_id == game_id)\
            .filter(Crime.status == "solved").count()

        return cnt

    def get_commited(self, game_id):
        cnt = cherrypy.request.db.query(Crime).filter(Crime.game_id == game_id)\
            .filter(or_(Crime.status == "commited", Crime.status == "solved")).count()

        return cnt

    def get_gap(self, game_id):
        #TODO implement gap change logic
        gap = 2
        next_gap = 3
        next_gap_time = timedelta(minutes=10)

        return gap, next_gap, next_gap_time

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def gap(self, game_id = None):
        if game_id is None:
            user, role, game, all_tasks = get_session_info()
            game_id = game.id

        gap, next_gap, next_gap_time = self.get_gap(game_id)
        return {"gap":gap, "next_gap":next_gap, "next_gap_time":next_gap_time.seconds}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delta(self, game_id = None):
        if game_id is None:
            user, role, game, all_tasks = get_session_info()
            game_id = game.id

        return {"delta":self.get_delta(game_id)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def hunt_status(self, game_id = None):
        if game_id is None:
            user, role, game, all_tasks = get_session_info()
            game_id = game.id

        gap, dummy1, dummy2 = self.get_gap(game_id)
        delta = self.get_delta(game_id)

        solved_cnt = self.get_solved(game_id)

        if delta <= gap and solved_cnt > 0:
            user, role, game, all_tasks = get_session_info()

            if role.role == "mrx":
                return {"hunt_active":True}
            else:
                loc = cherrypy.request.db.query(Location).join(Game)\
                    .join(Role, Role.user_id == Location.user_id)\
                    .filter(Game.id == game_id)\
                    .filter(Role.role == "mrx").order_by(Location.time.desc()).all()[0]

                return {"hunt_active":True, "lat":loc.lat, "lng":loc.lng, "time":str(loc.time)}
        else:
            return {"hunt_active":False}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def game_status(self, game_id = None):
        if game_id is None:
            user, role, game, all_tasks = get_session_info()
            game_id = game.id

        game = cherrypy.request.db.query(Game).filter(Game.id == game_id).one()

        ret = {}
        if game.start + game.duration > datetime.now():
            remaining = (game.start + game.duration - datetime.now()).seconds
            ret["remaining"] = remaining
        else:
            game.status = "finished"

        ret["game_status"] = game.status

        cherrypy.request.db.add(game)
        cherrypy.request.db.commit()

        return ret

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    @cherrypy.tools.allow(methods=['POST'])
    def submit_mrx_code(self, code):
        user, role, game, all_tasks = get_session_info()

        if role.role != "detective":
            return {"status":"fail", "msg":"only detectives can submit code"}

        if game.status != "active":
            return {"status":"fail", "msg":"game is not active"}

        if code == game.code:
            game.status = 'finished'
            cherrypy.request.db.add(game)
            cherrypy.request.db.commit()

            return {"status":"success"}
        else:
            return {"status":"fail", "msg":"wrong code"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def mrx_pos(self):
        user, role, game, all_tasks = get_session_info()

        gap, next_gap, next_gap_time = self.get_gap(game.id)
        delta = self.get_delta(game.id)

        if delta > gap:
            return {"status":"declined", "msg":"too big delta"}
        else:
            loc = cherrypy.request.db.query(Location).join(Game).join(Role)\
                .filter(Role.role == "mrx").order_by(Location.time.desc()).one()

            return {"status":"success", "lat":loc.lat, "lng":loc.lng, "time":loc.time}



    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    @require()
    def send_location(self, lat, lng):
        user, role, game, all_tasks = get_session_info()

        location = Location(
            user_id = user.id,
            game_id = game.id,
            lat = lat,
            lng = lng,
            time = datetime.now()
        )

        cherrypy.request.db.add(location)
        cherrypy.request.db.commit()

        return {"status":"success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['POST'])
    def make_newgame(self, players, mrx_pos, code="code"):
        if type(players) != list or len(players) < 2:
            return {"status": "fail", "msg": "Not enough players"}

        mrx_username = players[int(mrx_pos)]

        try:
            game = Game(status="active", code=code, start=datetime.now(), duration=timedelta(hours=2, minutes=30))
            cherrypy.request.db.add(game)

            #create roles
            for player in players:
                users = cherrypy.request.db.query(User).filter(User.username == player).all()

                if len(users) > 1:
                    raise cherrypy.HTTPError(500, "more than one user with given username")
                elif len(users) == 0:
                    # cherrypy.request.db.rollback()
                    return {"status":"fail", "msg":"No user found %s" % player}
                else:
                    user = users[0]

                active_games = cherrypy.request.db.query(Game).join(Game.roles).filter(
                    Game.status == "active").filter(Role.user_id == user.id).all()

                if len(active_games) > 0:
                    # cherrypy.request.db.rollback()
                    return {"status":"fail", "msg":"User %s already has active game" % player}

                if player == mrx_username:
                    role_name = "mrx"
                else:
                    role_name = "detective"

                role = Role(user_id=user.id, game=game, role=role_name)
                cherrypy.request.db.add(role)

            #create tasks
            photo_points = cherrypy.request.db.query(Point).all()
            for point in photo_points:
                mrx_task = Task(game=game, status="pending")
                det_task = Task(game=game, status="unavailable")

                crime = Crime(
                    game_id=game.id,
                    point_id=point.id,
                    center_lat=point.lat,
                    center_lng=point.lng,
                    radius=point.radius,
                    status="not_commited",
                    mrx_task=mrx_task,
                    det_task=det_task
                )

                mrx_task.crime = crime
                det_task.crime = crime

                cherrypy.request.db.add(mrx_task)
                cherrypy.request.db.add(det_task)
                cherrypy.request.db.add(crime)

            cherrypy.request.db.commit()
            return {"status": "success"}
        except Exception:
            cherrypy.request.db.rollback()
            raise



