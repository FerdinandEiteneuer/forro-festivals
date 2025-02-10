import os
import subprocess

from flask import Blueprint
from flask import render_template, request, redirect, url_for, current_app
import flask_login

from forro_festivals.models.event import Event
from forro_festivals import config, logger
from forro_festivals.routes import auth
from forro_festivals.db.db_api import get_events_from_db, get_event_from_db_by_id, update_event_by_id

bp = Blueprint('admin', __name__)


@bp.route('/dashboard')
@flask_login.login_required
def dashboard():
    events = get_events_from_db()
    event_list = [event.model_dump() for event in events]
    return render_template('dashboard.html', events=event_list)

@bp.route('/update-event', methods=['GET', 'POST'])
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

    event_id = int(event_data.pop('id'))

    try:
        event = get_event_from_db_by_id(event_id=event_id)
        event = Event.merge(event, partial_data=event_data)
        logger.info(f'event after merge:{event}')
        update_event_by_id(event_id=event_id, event=event)
    except Exception as e:
        logger.error(f'Exception during update_event: {e}. {event_id=}, {event_data=}, {event=}')

    return redirect(url_for('admin.dashboard'))

@bp.route('/dashboard-update-event', methods=['POST'])
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
            url_for('admin.update_event'),
            json=event_data
        )
    return redirect(url_for('admin.dashboard'))




@bp.route(f'/reload-bash', methods=['POST'])
@auth.permissions_required(['reload'])
def reload_bash():
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