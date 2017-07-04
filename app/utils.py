__author__ = 'ffuuugor'
import cherrypy
from app.models import *


def _last_game():
    active_games = cherrypy.request.db.query(Game) \
        .filter(Game.status == "active") \
        .order_by(Game.created.desc()) \
        .all()

    if active_games:
        return active_games[0]

    all_games = cherrypy.request.db.query(Game) \
        .order_by(Game.created.desc()) \
        .all()

    if all_games:
        return all_games[0]
    else:
        return None


def _tasks_by_game(game):
    return cherrypy.request.db.query(Task, Point).filter(Task.game_id == game.id).join(Point).all()


def get_session_info():
    game = _last_game()
    if not Game:
        return None, None

    tasks = _tasks_by_game(game)
    return game, tasks

