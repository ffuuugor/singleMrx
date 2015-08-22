__author__ = 'ffuuugor'
import cherrypy
from app.models import *
from auth import SESSION_KEY

def get_session_info():
    username = cherrypy.session.get(SESSION_KEY)

    user = cherrypy.request.db.query(User).filter(User.username == username).one()
    all_games = cherrypy.request.db.query(Role, Game).join(Game.roles)\
        .filter(Role.user_id == user.id)\
        .order_by(Game.start.desc())\
        .all()

    if len(all_games) == 0:
        return user, None, None, None

    role, game = all_games[0]

    if role.role == "mrx":
        all_tasks = cherrypy.request.db.query(Task, Crime, Point)\
            .join(Crime, Crime.mrx_task_id == Task.id)\
            .join(Point)\
            .filter(Crime.game_id == game.id).all()
    elif role.role == "detective":
        all_tasks = cherrypy.request.db.query(Task, Crime, Point)\
            .join(Crime, Crime.det_task_id == Task.id)\
            .join(Point)\
            .filter(Crime.game_id == game.id).all()

    return user, role, game, all_tasks
