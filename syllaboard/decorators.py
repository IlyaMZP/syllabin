from functools import wraps

from flask import flash, url_for, redirect
from flask_login import current_user


def headman_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_headman:
            flash('Not enough permissions.', 'warning')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorated_function


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Not enough permissions.', 'warning')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorated_function
