from flask import render_template, redirect, url_for, flash, request, abort
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email, send_confirm_email
from jwt.exceptions import InvalidTokenError
from app.auth.decorators import check_confirmed


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Вы уже авторизовались!', 'success')
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный email или пароль. Попробуйте еще раз!', 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember.data)
        if not request.args.get('next'):
            return redirect(url_for('main.index'))
        next_page = request.args.get('next')
        if url_parse(next_page).scheme != '' or url_parse(next_page).netloc != '':
            return abort(400)
        return redirect(next_page)
    return render_template('auth/login.html', title='Авторизация', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из своего аккаунта. До скорых встреч!')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            user = User(
                first_name=form.first_name.data,
                second_name=form.second_name.data,
                email=form.email.data,
                password=form.password.data,
                gender=form.gender.data,
                phone_number=form.phone_number.data,
            )
            db.session.add(user)
            db.session.commit()
            send_confirm_email(user)
            login_user(user)
            flash('Подтвердите свой email. На указанную почту отправлено письмо', 'success')
            return redirect(url_for('auth.unconfirmed'))
        except:
            db.session.rollback()

    return render_template('auth/register.html', title='Регистрация',
                           form=form)


@bp.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = User.confirm_token(token)
        user = User.query.filter_by(email=email).first()
    except InvalidTokenError:
        flash('Подтверждающая ссылка просрочена или повреждена', 'danger')
        return redirect(url_for('auth.login'))

    if user.email_confirmed:
        flash('Ваш аккаунт уже подтвержден!', 'success')
    else:
        user.email_confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Аккаунт подтвержден. Спасибо!', 'success')
    return redirect(url_for('user.profile'))


@bp.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.email_confirmed:
        return redirect('main.index')
    flash('Пожалуйста, подтвердите свой аккаунт!', 'warning')
    return render_template('auth/unconfirmed.html')


@bp.route('/resend')
@login_required
def resend_confirmation():
    send_confirm_email(current_user)
    flash('Новое подтверждение было отправлено на Вашу почту', 'success')
    return redirect(url_for('auth.unconfirmed'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.email_confirmed:
            send_password_reset_email(user)
            flash('На указанный email были отправлены инструкции по восстановлению пароля', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Пользователя с таким подтвержденным email не существует!', 'info')

    return render_template('auth/reset_password_request.html',
                           title='Сброс пароля', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    try:
        user = User.verify_reset_password_token(token)
    except InvalidTokenError:
        flash('Подтверждающая ссылка просрочена или повреждена', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль был обновлён!')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, title='Новый пароль')
