__author__ = 'ffuuugor'
import cherrypy
import os
from app.db.sqlalchemy_plugin import SQLAlchemyPlugin
from app.db.sqlalchemy_tool import SQLAlchemyTool
from app.models import Base
from app.auth import AuthController
from app.api import Api
from app.task_api import TaskApi
from app.view import View

def http_methods_allowed(methods=['GET', 'HEAD']):
    method = cherrypy.request.method.upper()
    if method not in methods:
        cherrypy.response.headers['Allow'] = ", ".join(methods)
        raise cherrypy.HTTPError(405)

PATH = os.path.abspath(os.path.dirname(__file__))
if __name__ == '__main__':
    cherrypy.config.update('app.conf')

    #recreate symlink to data dir
    uploads_dir = os.path.join(PATH,"static","image","uploads")
    if os.path.exists(uploads_dir):
        os.remove(uploads_dir)
    os.symlink(cherrypy.config["mrx.uploads.dir"], uploads_dir)


    cherrypy.tools.db = SQLAlchemyTool()
    cherrypy.tools.allow = cherrypy.Tool('on_start_resource', http_methods_allowed)

    plugin = SQLAlchemyPlugin(
        cherrypy.engine, Base, cherrypy.config["mrx.db.uri"]
    )

    plugin.create()
    plugin.subscribe()

    cherrypy.tree.mount(View(), '/', 'app.conf')
    cherrypy.tree.mount(Api(), '/api', 'app.conf')
    cherrypy.tree.mount(TaskApi(), '/api/task', 'app.conf')
    cherrypy.tree.mount(AuthController(), '/auth', 'app.conf')

    cherrypy.engine.start()
    cherrypy.engine.block()
