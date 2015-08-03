__author__ = 'ffuuugor'
import cherrypy
from app.simpleserver import HelloWorld
import os

if __name__ == '__main__':
    conf = {
        'global': { 'server.environment': 'production',
                      'server.socket_host': '0.0.0.0',
                      'server.socket_port': 80,
        },
        '/': {
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
    cherrypy.quickstart(HelloWorld(), '/', conf)
