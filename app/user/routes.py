from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

from app import db
from app.user import bp
from app.user.forms import UpdateAccountForm
from app.models import Users


@bp.route('/profile')
@login_required
def profile():
    user = Users.query.filter_by(id=current_user.id).first()
    form = UpdateAccountForm()

    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.second_name.data = current_user.second_name
        form.email.data = current_user.email
        '''
    elif form.validate_on_submit():
        
        path_one = os.path.join(os.getcwd(), UPLOAD_FOLDER, user.username)
        path_two = os.path.join(os.getcwd(), UPLOAD_FOLDER, form.username.data)
        os.rename(path_one, path_two)
        current_user.username = form.username.data
        current_user.email = form.email.data

        current_user.user_status = form.user_status.data

        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data, user)
        else:
            form.picture.data = current_user.image_file

        db.session.commit()
        
        flash('Ваш аккаунт был обновлён!', 'success')
        return redirect(url_for('users.profile'))
'''
    return render_template('user/profile.html', title='Аккаунт',
                           form=form, user=user)
