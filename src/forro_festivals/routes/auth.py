from functools import wraps
from typing import List

from flask import Blueprint
from flask import render_template, request, redirect, url_for, session
import flask_login

from forro_festivals.db import db_api
from forro_festivals import logger
from forro_festivals.misc.passwords import verify_password

bp = Blueprint('auth', __name__)

login_manager = flask_login.LoginManager()
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def user_loader(id):
    return db_api.get_user(id)

@login_manager.request_loader
def request_loader(request):
    id = request.form.get('id')
    return db_api.get_user(id)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if next_url := request.args.get('next'):
            session['next'] = next_url
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        user = db_api.get_user_by_email(email)
        logger.debug(f'user {email} is trying to login')
        if user and verify_password(request.form['password'], user.hashed_pw):
            flask_login.login_user(user)
            logger.info(f'User {user.email} just logged in')
            if next_url := session.pop('next', None):
                logger.info(f'redirecting to {next_url=}')
                return redirect(next_url)
            logger.info(f'simply redirecting to dashboard - fallback')
            return redirect(url_for('admin.dashboard'))
        return 'Unauthorized', 403


@bp.route('/logout')
def logout():
    if flask_login.current_user.is_authenticated:
        logger.info(f'User {flask_login.current_user.id} is logging out')
        flask_login.logout_user()
        return redirect(url_for('info.festivals'))
    else:
        return 'Very funny, but you are not logged in'


def permissions_required(permissions: List[str]):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            user = flask_login.current_user
            if set(permissions).issubset(user.permission_set):
                logger.info(f'{user.permissions=}')
                logger.info(f'{permissions=}')
                return fn(*args, **kwargs)
            else:
                return f'That route is forbidden for user "{user.id}"', 403
        return decorated_view
    return wrapper
