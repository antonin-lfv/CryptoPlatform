from flask import Flask, render_template
from configuration.config import Config as app_config
from flask_login import LoginManager

from auth.auth import BLP_auth
from general.general import BLP_general
from flask_sqlalchemy import SQLAlchemy
from os import path


db = SQLAlchemy()


def create_app():
    # ===== Flask app
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(app_config)
    # ===== Blueprint
    app.register_blueprint(BLP_auth)
    app.register_blueprint(BLP_general)
    # ===== init SQLAlchemy
    db.init_app(app)
    if not path.exists("db.sqlite"):
        with app.app_context():
            db.create_all()
    # ===== Login manager
    login_manager = LoginManager()
    login_manager.login_view = 'BLP_auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # ===== error page
    @app.errorhandler(404)
    def forbidden(error):
        return render_template('errors/error_404.html')

    return app


app = create_app()
