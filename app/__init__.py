from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_mail import Mail


db = SQLAlchemy()
bootstrap = Bootstrap5()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'info'

mail = Mail()

def create_data(load_company):
    from app.load_data import LoadData
    data = LoadData(load_company=load_company)
    data.create_data()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    #migrate.init_app(app, db, render_as_batch=True)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.company import bp as company_bp
    app.register_blueprint(company_bp, url_prefix='/company')

    return app