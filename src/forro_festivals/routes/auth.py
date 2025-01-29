import json
from functools import wraps
from typing import List, Set

from flask import Blueprint
from flask import render_template, request, redirect, url_for, session
import flask_login

from forro_festivals.scripts.logger import logger
import forro_festivals.config as config

bp = Blueprint('auth', __name__)

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

# TODO: yes, storing this in a json is just temporary
users = load_json(config.users_path)

class User(flask_login.UserMixin):
    def __init__(self, id: str, permissions: List[str]):
        self.id = id
        self.permissions = permissions


login_manager = flask_login.LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def user_loader(id):
    logger.info('user loader called')
    if id not in users:
        return None
    return User(id=id, permissions=users[id]['permissions'])

@login_manager.request_loader
def request_loader(request):
    logger.info(f'request loader called {dict(request.form)=}, {dict(request.args)=}')
    id = request.form.get('id')
    if id not in users:
        return None
    return User(id=id, permissions=users[id]['permissions'])

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if next_url := request.args.get('next'):
            session['next'] = next_url
        return render_template('login.html')
    elif request.method == 'POST':
        id = request.form['id']
        if id in users and request.form['password'] == users[id]['password']:
            user = User(id=id, permissions=users[id]['permissions'])
            flask_login.login_user(user)
            logger.info(f'User {user.id} just logged in')
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
            if set(permissions).issubset(user.permissions):
                logger.info(f'{user.permissions=}')
                logger.info(f'{permissions=}')
                return fn(*args, **kwargs)
            else:
                return f'That route is forbidden for user "{user.id}"', 403
        return decorated_view
    return wrapper
