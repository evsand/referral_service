from flask import render_template
from app.main import bp
from app import login_manager
from app.models import Users


@bp.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

##################################################################
##################### Delete me please ###########################
##################################################################

from flask import jsonify

@bp.route('/test')
def test():
    return jsonify({'seccesfull': 'response'})

'''
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index_old.html', title='Home')


@bp.route('/user/<username>')
@login_required
def user(username):
    user = Users.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

'''