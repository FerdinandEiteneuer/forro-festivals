import json
import subprocess
import os
import logging

from pydantic import ValidationError
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, current_app, url_for, session
import flask_login

import forro_festivals.config as config
from forro_festivals.scripts.logger import get_logger
from forro_festivals.scripts.create_festivals_html import create_festivals_html
from forro_festivals.scripts.db import get_events_from_db, get_event_from_db_by_id, update_event_by_id, add_event_to_db
from forro_festivals.scripts.event import Event
from forro_festivals.scripts.notification import post_event_to_ntfy_channel

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

logger = get_logger()

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

users = load_json(config.users_path)

class User(flask_login.UserMixin):
    pass

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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        config.static_folder / 'favicons',
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/')
def festivals():
    return app.send_static_file('festivals.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/legal-notice')
def legal_notice():
    return app.send_static_file('legal-notice.html')

@app.route(f'/reload-bash', methods=['POST'])
def reload_bash():
    api_token = request.authorization.token
    if api_token != config.API_TOKEN:
        logger.warning(f'bad api token supplied')
        return 'Unauthorized', 403

    if request.method == 'POST':
        try:
            os.chdir(config.root_path_repository)

            # Perform a git pull
            result = subprocess.run(['bash', 'src/forro_festivals/scripts/reload-all.sh'], capture_output=True, text=True, check=True)
            stdout, stderr = result.stdout, result.stderr

            if result.returncode == 0:
                return 'Deployment successfull', 200
            else:
                err_str = f'Deployment failed: {stdout=}, {stderr=}'
        except Exception as e:
            err_str = f"Exception during reloading: {str(e)}"

        logger.error(err_str)
        return err_str, 500

@app.route('/add-festival', methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        return render_template("add-festival.html", data={}), 200
    elif request.method == "POST":
        try:
            logger.info(request.form)
            event = Event.from_request(request)
        except ValidationError as exc:
            err_msg = Event.human_readable_validation_error_explanation(exc)
            return jsonify({'error': err_msg}), 400

        try:
            new_id = add_event_to_db(event)
        except Exception as e:
            logger.error(f'Could not save {event=} into database {e=}')
            return jsonify({'error': 'Could not save into database'}), 500

        if new_id != 0:
            ntfy_response = post_event_to_ntfy_channel(event, event_id=new_id, topic=config.NTFY_TOPIC)
            if ntfy_response.status_code > 200:
                logger.warning(f'{ntfy_response.status_code=}, {ntfy_response.text=}')

            success_msg = f'Event saved successfully! 🎉<br>Preview:<br>{event.to_html_string()}'
            return jsonify({'html_msg': success_msg}), 200
        elif new_id == 0:
            return jsonify({'error': 'Entry is duplicated'}), 400



@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info(f'called login with {request.args.get("next")=} and {request.method=}. {session.get("next")=}')
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

@app.route('/logout')
def logout():
    logger.info(f'User {flask_login.current_user.id} is logging out')
    flask_login.logout_user()
    return redirect(url_for('festivals'))

@app.route('/dashboard')
@flask_login.login_required
def dashboard():
    events = get_events_from_db()
    event_list = [event.model_dump() for event in events]
    return render_template('dashboard.html', events=event_list)

@app.route('/update-event', methods=['GET', 'POST'])
@flask_login.login_required
def update_event():
    # Note: Currently the intended use of this function is to work properly
    #       with the dashboard, which can update database entries.
    logger.info(f'user {flask_login.current_user.id} is updating an event')

    if request.method == 'POST':
        event_data = request.get_json()
    elif request.method == 'GET':
        logger.info(f'GET: {dict(request.args)=}')
        event_data = dict(request.args)

    event_id = event_data.pop('id')

    try:
        event = get_event_from_db_by_id(event_id=event_id)
        event = Event.merge(event=event, partial_data=event_data)
        update_event_by_id(event_id=event_id, event=event)
        logger.info('recreating festivals.html ...')
        create_festivals_html()
    except Exception as e:
        logger.error(f'Exception during update_event: {e}. {event_id=}, {event_data=}, {event=}')

    return redirect(url_for('dashboard'))

@app.route('/dashboard-update-event', methods=['POST'])
@flask_login.login_required
def dashboard_update_event():
    # Note: Currently the intended use of this function is to work properly
    #       with the dashboard, which can update database entries.
    logger.info(f'{flask_login.current_user.id} updated an event')

    event_data = {
        key.split('|')[0]: value
        for key, value in dict(request.form).items()
    }
    logger.info(f'received {dict(request.form)}, sending {event_data}')

    with current_app.test_client() as client:
        client.post(
            url_for('update_event'),
            json=event_data
        )
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
