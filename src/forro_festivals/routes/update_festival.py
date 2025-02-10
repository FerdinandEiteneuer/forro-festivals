from flask import request, render_template, jsonify, Blueprint, redirect
from pydantic import ValidationError

from forro_festivals import config, logger
from forro_festivals.scripts.create_festivals_html import format_event, create_festival_data, \
    format_festival_data_short, create_festival_data_short
from forro_festivals.scripts.db_api import add_event_to_db
from forro_festivals.scripts.event import Event
from forro_festivals.scripts.notification import post_event_to_ntfy_channel

bp = Blueprint('update-festival', __name__)


@bp.route('/update-festival', methods=['GET', 'POST'])
def update_festival():
    festivals_short = create_festival_data_short()
    if request.method == 'GET':
        return render_template(template_name_or_list='update-festival.html', festivals_short=festivals_short), 200
    elif request.method == "POST":
        logger.info(f'We received POST: {request.form}')
        return render_template(template_name_or_list='update-festival.html', festivals_short=festivals_short), 200
