__author__ = 'ffuuugor'

import cherrypy
import hashlib
from models import User, Token
import random
import string
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('view'))

SESSION_KEY = '_mrx_username'

def hashpass(password):
    return hashlib.md5(password).hexdigest()

def check_credentials(username, password):
    try:
        user = cherrypy.request.db.query(User).filter(User.username == username).one()
        if hashpass(password) == user.password:
            return user
        else:
            return None
    except:
        return None

def check_auth(*args, **kwargs):
    # if cherrypy.request.config.get('auth.require', None) is None:
    #     return

    token = cherrypy.request.params.get("token", None)

    if token is not None:

        cherrypy.request.params.pop("token", None)

        usernames = cherrypy.request.db.query(Token).filter(Token.token == token).all()

        if len(usernames) == 1:
            cherrypy.request.login = usernames[0].user.username
        elif len(usernames) > 1:
            raise Exception()
        else:
            raise cherrypy.HTTPRedirect("/auth/login")
        # username = cherrypy.session.get(SESSION_KEY)
        # if username:
        #     cherrypy.request.login = username
        #     for condition in conditions:
        #         # A condition is just a callable that returns true or false
        #         if not condition():
        #             raise cherrypy.HTTPRedirect("/auth/login")
        # else:
        #     raise cherrypy.HTTPRedirect("/auth/login")

cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

class AuthController(object):

    @cherrypy.expose()
    def register(self, username=None, phone=None, password=None):
        if username is None or phone is None or password is None:
            return env.get_template('register.html').render()
        else:
            user = User(username=username, phone=phone, password=hashpass(password))

            cherrypy.request.db.add(user)
            cherrypy.request.db.commit()

            self.login(username=username, password=password)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def login(self, username=None, password=None):
        user = check_credentials(username, password)
        if user is None:
            return {"status":"fail"}
        else:
            token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))

            token_obj = Token(user=user, token=token)
            cherrypy.request.db.add(token_obj)
            cherrypy.request.db.commit()
            return {"status":"success", "token":token}

    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
        raise cherrypy.HTTPRedirect(from_page or "/")
