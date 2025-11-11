from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
import logging
import time

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # route name for login
    login_manager.login_view = 'main.login'  # means @login_required will redirect to main.login

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.Formatter.converter = time.gmtime  # UTC timestamps for log entries
    handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)

    # prevent duplicate logs when debug auto-reloads
    if not app.logger.handlers:
        app.logger.addHandler(handler)

    # import routes after extensions, avoiding circular imports
    from .routes import main
    app.register_blueprint(main)

    return app

# import User after db is defined so models can import db without circles
from .models import User

# user loader used by flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # needed for session handling