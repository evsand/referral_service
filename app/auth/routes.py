from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
from app.models import Users
from app.auth.email import send_password_reset_email, send_confirm_email
from app.auth.decorators import check_confirmed


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Авторизация', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(
            first_name=form.first_name.data,
            second_name=form.second_name.data,
            email=form.email.data,
            gender=form.gender.data,
            phone_number=form.phone_number.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_confirm_email(user)

        login_user(user)

        flash('Подтвердите свой email. На указанную почту отправлено письмо', 'success')

        return redirect(url_for('auth.unconfirmed'))

    return render_template('auth/register.html', title='Регистрация',
                           form=form)


@bp.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = Users.confirm_token(token)
    except:
        flash('Подтверждающая ссылка просрочена', 'danger')
    user = Users.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Ваш аккаунт уже подтвержден. Пожалуйста, авторизуйтесь!', 'success')
        return redirect(url_for('auth.login'))
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Аккаунт подтвержден. Спасибо!', 'success')
    return redirect(url_for('main.index'))


@bp.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('main.home')
    flash('Please confirm your account!', 'warning')
    return render_template('auth/unconfirmed.html')


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('На указанный email были отправлены инструкции по восстановлению пароля', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Пользователя с таким email не существует!', 'info')

    return render_template('auth/reset_password_request.html',
                           title='Сброс пароля', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = Users.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль был обновлён!')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, title='Новый пароль')
