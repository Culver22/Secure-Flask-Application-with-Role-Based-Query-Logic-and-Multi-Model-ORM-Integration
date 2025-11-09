from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from .models import User

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # route name for login
    login_manager.login_view = 'main.login'  # means @login_required will redirect to main.login

    from .routes import main
    app.register_blueprint(main)

    return app

# user loader used by flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # needed for session handling