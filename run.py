__author__ = 'ffuuugor'
import cherrypy
from app.simpleserver import HelloWorld
import os
from cp_sqlalchemy import SQLAlchemyTool, SQLAlchemyPlugin
from app.models import Base
from settings import DB_URI

def http_methods_allowed(methods=['GET', 'HEAD']):
    method = cherrypy.request.method.upper()
    if method not in methods:
        cherrypy.response.headers['Allow'] = ", ".join(methods)
        raise cherrypy.HTTPError(405)

if __name__ == '__main__':
    global_conf =  {
        'global': {
            'server.environment': 'production',
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 80,
        }
    }

    conf = {
        '/': {
            'tools.db.on': True,
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '.',
            'tools.staticdir.index': 'view/index.html',
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        }
    }
    cherrypy.config.update(global_conf)
    cherrypy.tools.db = SQLAlchemyTool()
    cherrypy.tools.allow = cherrypy.Tool('on_start_resource', http_methods_allowed)

    SQLAlchemyPlugin(
        cherrypy.engine, Base, DB_URI
    ).subscribe()

    cherrypy.tree.mount(HelloWorld(), '/', conf)

    cherrypy.engine.start()
    cherrypy.engine.block()
