__author__ = 'ffuuugor'
import cherrypy
from app.simpleserver import HelloWorld
import os
from cp_sqlalchemy import SQLAlchemyTool, SQLAlchemyPlugin
from app.models import Base

if __name__ == '__main__':
    conf = {
        'global': { 'server.environment': 'production',
                      'server.socket_host': '0.0.0.0',
                      'server.socket_port': 80,
        },
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
    cherrypy.tools.db = SQLAlchemyTool()

    SQLAlchemyPlugin(
        cherrypy.engine, Base, 'postgres://localhost:5432/'
    ).subscribe()

    cherrypy.tree.mount(HelloWorld(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
