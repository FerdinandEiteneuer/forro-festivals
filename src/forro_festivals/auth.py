import json

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
    pass

login_manager = flask_login.LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if next_url := request.args.get('next'):
            session['next'] = next_url
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        if email in users and request.form['password'] == users[email]['password']:
            user = User()
            user.id = email
            flask_login.login_user(user)
            logger.info(f'User {email} just logged in')
            if next_url := session.pop('next', None):
                logger.info(f'redirecting to {next_url=}')
                return redirect(next_url)
            logger.info(f'simply redirecting to dashboard - fallback')
            return redirect(url_for('dashboard'))
        return 'Unauthorized', 403

@bp.route('/logout')
def logout():
    logger.info(f'User {flask_login.current_user.id} is logging out')
    flask_login.logout_user()
    return redirect(url_for('festivals'))
