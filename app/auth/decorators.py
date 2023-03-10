from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.email_confirmed is False:
            flash('Пожалуйста, подсвердите свой аккаунт!', 'warning')
            return redirect(url_for('auth.unconfirmed'))
        return func(*args, **kwargs)
    return decorated_function
