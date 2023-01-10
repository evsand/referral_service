from flask import render_template
from app.main import bp
from app import login_manager
from app.models import User


@bp.route('/')
def index():

    return render_template('index.html')


'''
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
'''