import json
import subprocess
import os

from pydantic import ValidationError
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, current_app, url_for

import flask_login

from forro_festivals.scripts.create_impressum_html import create_impressum_html
import forro_festivals.config as config
from forro_festivals.scripts.db import get_events_from_db, get_event_from_db_by_id, update_event_by_id, add_event_to_db
from forro_festivals.scripts.event import Event


def prepare():
    create_impressum_html()


app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']  # TODO make env var

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

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

festivals_data = {
    "June 2024": [
        {
            "location": "Porto, Portugal",
            "date_start": "01.06",
            "date_end": "02.06",
            "link": "https://example.com/festival-internacional-de-forro",
            "link_text": "Festival Internacional de Forró"
        },
        {
            "location": "Berlin, Germany",
            "date_start": "07.06",
            "date_end": "09.06",
            "link": "https://example.com/berlin-tome-forro",
            "link_text": "Berlin – Tome Forró"
        },
        {
            "location": "Karlsruhe, Germany",
            "date_start": "07.06",
            "date_end": "09.06",
            "link": "https://example.com/forro-de-ka",
            "link_text": "Forró de KA Festival"
        }
    ],
    "July 2024": [
        {
            "location": "Stockholm, Sweden",
            "date_start": "05.07",
            "date_end": "07.07",
            "link": "https://example.com/alegria-do-norte",
            "link_text": "Alegria do Norte"
        },
        {
            "location": "Leisnig, Germany",
            "date_start": "12.07",
            "date_end": "14.07",
            "link": "https://example.com/forro-experience",
            "link_text": "Forró Experience"
        }
    ]
}


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(config.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def festivals():
    return app.send_static_file('festivals.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/impressum')
def impressum():
    return app.send_static_file('impressum.html')

@app.route(f'/reload-bash', methods=['POST'])
def reload_bash():

    api_token = request.authorization.token
    if api_token != config.API_TOKEN:
        app.logger.warning(f'bad api token supplied')
        return "Unauthorized", 403

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

        print(err_str)
        return err_str, 500

@app.route('/add-festival', methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        return render_template("add-festival.html", data={}), 200
    elif request.method == "POST":
        app.logger.info(f'button press?')
        try:
            app.logger.info(request.form)
            event = Event.from_request(request)
        except ValidationError as exc:
            err_msg = Event.human_readable_validation_error_explanation(exc)
            return jsonify({'error': err_msg}), 400

        try:
            add_event_to_db(event)
            success_msg = f'Event saved successfully! 🎉<br>Preview:<br>{event.to_html_string()}'
            return jsonify({'html_msg': success_msg}), 200
        except Exception as e:
            app.logger.error(f'Could not save {event=} into database')
            return jsonify({'html_msg': 'Unknown Error'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form['email']
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('dashboard'))
    return 'Unauthorized'


@app.route('/dashboard')
@flask_login.login_required
def dashboard():
    events = get_events_from_db()
    event_list = [event.model_dump() for event in events]
    return render_template('dashboard.html', events=event_list)

@app.route('/update-event', methods=['POST'])
@flask_login.login_required
def update_event():
    # Note: Currently the intended use of this function is to work properly
    #       with the dashboard, which can update database entries.
    app.logger.info(dict(request.form))
    event_data = {
        key.split('|')[0]: value
        for key, value in dict(request.form).items()
    }
    event_id = event_data.pop('id')

    try:
        event = get_event_from_db_by_id(event_id=event_id)
        event.update(event_data=event_data)
        update_event_by_id(event_id=event_id, event=event)
    except Exception as e:
        app.logger.info(f'Exception during update_event: {e}. {event_id=}, {event_data=}, {event=}')


    app.logger.info('reloading app...')
    # Trigger the "reload-bash" route programmatically using Flask's test_client()
    with current_app.test_client() as client:
        response = client.post(
            url_for('reload_bash'),
            headers={'Authorization': f'Token {config.API_TOKEN}'}
        )  # Trigger the reload-bash route
    app.logger.info(f'reloading app route executed, {response.status_code=}')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    prepare()
    app.run(debug=True)
