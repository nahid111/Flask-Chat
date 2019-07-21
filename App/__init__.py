import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_login import LoginManager
from flask_socketio import SocketIO


# ===================================================================
#                          instantiate app
# ===================================================================
app = Flask(__name__)
app.config.from_object('Config.config.DevelopmentConfig')
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app)


# ===================================================================
#                       flask-login settings
# ===================================================================
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # route to login page
login_manager.session_protection = "strong"
login_manager.init_app(app)


# ===================================================================
#                       File upload directories
# ===================================================================
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPOLAD_DIRECTORY = os.path.join(APP_ROOT, "static/uploads/")
AVATAR_UPOLAD_DIRECTORY = os.path.join(UPOLAD_DIRECTORY, "avatars/")
if not os.path.isdir(AVATAR_UPOLAD_DIRECTORY):
    os.mkdir(AVATAR_UPOLAD_DIRECTORY)


# ===================================================================
#                 import & register View blueprints
# ===================================================================
from App.auth.views.auth_views import auth_views_module
app.register_blueprint(auth_views_module)

from App.site.views.site_index_views import site_index_views_module
from App.site.views.site_chat_views import site_chat_views_module

app.register_blueprint(site_index_views_module)
app.register_blueprint(site_chat_views_module)


