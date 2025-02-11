from flask import request, render_template, Blueprint, flash

from forro_festivals import logger
from forro_festivals.models import Suggestion
from forro_festivals.scripts.create_festivals_html import create_festival_data_short
from forro_festivals.db import db_api

bp = Blueprint('update-festival', __name__)


@bp.route('/update-festival', methods=['GET', 'POST'])
def update_festival():
    festivals_short = create_festival_data_short()
    if request.method == 'GET':
        return render_template(template_name_or_list='update-festival.html', festivals_short=festivals_short), 200
    elif request.method == "POST":
        try:
            logger.info(f'We received POST: {request.form} {dict(request.form)}')
            suggestion = Suggestion.from_request(request)
            db_api.insert(suggestion)
            flash('Received ... TODO', 'success')
        except Exception as e:
            logger.error(f'Something went wrong with creating a suggestion: {e}')
            flash(f'Sorry, something went wrong. 😔', 'error')

        return render_template(template_name_or_list='update-festival.html', festivals_short=festivals_short), 200
