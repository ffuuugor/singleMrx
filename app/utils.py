__author__ = 'ffuuugor'
import cherrypy
from app.models import *

def get_session_info():
    # username = cherrypy.session.get(SESSION_KEY)
    username = 'ttt'

    user = cherrypy.request.db.query(User).filter(User.username == username).one()
    role = cherrypy.request.db.query(Role).join(Game.roles).filter(
        Game.status == "active").filter(Role.user_id == user.id).one()
    game = cherrypy.request.db.query(Game).filter(Game.id == role.game_id).one()

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
