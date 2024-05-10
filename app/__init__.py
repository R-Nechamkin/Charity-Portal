from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from .config import Config


# init SQLAlchemy so we can use it later in our models
app = Flask('app')
app.config.from_object(Config)
db = SQLAlchemy(app)

migrate = Migrate(app, db)
login = LoginManager(app)


#variables

api_key = "AIzaSyDm3NkpUP7s2-9eIctdLS2OZzcYKWnVvXc"
api_url = "https://sheets.googleapis.com/v4/spreadsheets/{}?key=" + api_key



def create_app():

    login.login_view = 'auth.login'
    

    from .models import User


    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


create_app()

    