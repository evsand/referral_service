from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

from app import db
from app.user import bp
from app.user.forms import UpdateAccountForm
from app.models import User


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(id=current_user.id).first()
    form = UpdateAccountForm()

    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.second_name.data = current_user.second_name
        form.email.data = current_user.email
        form.gender = current_user.gender
        form.phone_number = current_user.phone_number


    elif form.validate_on_submit():
        # path_one = os.path.join(os.getcwd(), UPLOAD_FOLDER, user.username)
        # path_two = os.path.join(os.getcwd(), UPLOAD_FOLDER, form.username.data)
        # os.rename(path_one, path_two)
        current_user.first_name = form.first_name.data
        current_user.second_name = form.second_name.data
        current_user.email = form.email.data
        current_user.gender = form.gender.data
        current_user.phone_number = form.phone_number.data

        # if form.picture.data:
        #     current_user.image_file = save_picture(form.picture.data, user)
        # else:
        #     form.picture.data = current_user.image_file

        db.session.commit()
        
        flash('Ваш аккаунт был обновлён!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html', title='Аккаунт',
                           form=form, user=user)
