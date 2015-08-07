__author__ = 'ffuuugor'
import cherrypy
import os
from cp_sqlalchemy import SQLAlchemyTool, SQLAlchemyPlugin
from app.models import Base

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

    SQLAlchemyPlugin(
        cherrypy.engine, Base, cherrypy.config["mrx.db.uri"]
    ).subscribe()

    from app.simpleserver import HelloWorld
    cherrypy.tree.mount(HelloWorld(), '/', 'app.conf')

    cherrypy.engine.start()
    cherrypy.engine.block()
