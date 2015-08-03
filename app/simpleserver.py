__author__ = 'ffuuugor'
import cherrypy
import os

PATH = os.path.abspath(os.path.dirname(__file__))
class HelloWorld(object):
    pass
    # @cherrypy.expose
    # def index(self):
    #     return "Hello world!"

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': PATH,
            'tools.staticdir.index': 'index.html',
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.quickstart(HelloWorld(), '/', conf)
