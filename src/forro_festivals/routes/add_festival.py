from flask import request, render_template, jsonify, Blueprint, redirect
from pydantic import ValidationError

from forro_festivals import config, logger
from forro_festivals.scripts.create_festivals_html import format_event, create_festival_data, \
    format_festival_data_short, create_festival_data_short
from forro_festivals.scripts.db_api import add_event_to_db
from forro_festivals.scripts.event import Event
from forro_festivals.scripts.notification import post_event_to_ntfy_channel

bp = Blueprint('add-festival', __name__)

@bp.route('/add-festival', methods=['GET', 'POST'])
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
            if config.NTFY_TOPIC:
                ntfy_response = post_event_to_ntfy_channel(event, event_id=new_id, topic=config.NTFY_TOPIC)
                if ntfy_response.status_code > 200:
                    logger.warning(f'{ntfy_response.status_code=}, {ntfy_response.text=}')

            success_msg = f'Event saved successfully! 🎉<br>Preview:<br>{format_event(event)}'
            return jsonify({'html_msg': success_msg}), 200
        elif new_id == 0:
            return jsonify({'error': 'Entry is duplicated'}), 400

@bp.route('/update-next-lot', methods=['GET'])
def suggest_lot_date():
    festivals_short = create_festival_data_short()
    return render_template(template_name_or_list='update-next-lot.html', festivals_short=festivals_short)


