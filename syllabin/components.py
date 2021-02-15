#from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_avatars import Avatars
#from flask_mail import Mail
#from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
#from flask_migrate import Migrate


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
avatars = Avatars()
#ckeditor = CKEditor()
#mail = Mail()
#moment = Moment()
toolbar = DebugToolbarExtension()
#migrate = Migrate()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


@login_manager.user_loader
def load_user(user_id):
    from syllabin.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
# login_manager.login_message = 'Your custom message'
login_manager.login_message_category = 'warning'
