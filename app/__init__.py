from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5

import click



db = SQLAlchemy()
bootstrap = Bootstrap5()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'success'



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    #migrate = Migrate(app, db) #
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


    @app.cli.command("create-category")
    @click.argument("flag")
    def create_user(flag):
        from app.load_data import LoadData
        data = LoadData(flag)
        data.create_data()

    return app

