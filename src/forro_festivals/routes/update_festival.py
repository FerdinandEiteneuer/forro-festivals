from flask import request, render_template, Blueprint

from forro_festivals import logger
from forro_festivals.scripts.create_festivals_html import create_festival_data_short

bp = Blueprint('update-festival', __name__)


@bp.route('/update-festival', methods=['GET', 'POST'])
def update_festival():
    festivals_short = create_festival_data_short()
    if request.method == 'GET':
        return render_template(template_name_or_list='update-festival.html', festivals_short=festivals_short), 200
    elif request.method == "POST":
        logger.info(f'We received POST: {request.form}')
        return render_template(template_name_or_list='update-festival.html', festivals_short=festivals_short), 200
