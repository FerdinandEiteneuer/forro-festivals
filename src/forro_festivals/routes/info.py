"""
Routes for the ...
* festival list
* about page
* legal-notice (impressum)
* favicon
"""
import json

from flask import render_template, send_from_directory, Blueprint, current_app

from forro_festivals import config
from forro_festivals.scripts.create_festivals_html import create_festival_data

bp = Blueprint('info', __name__)


def load_json(path):
    """Saving Name+Location in a json not checked into the github repository."""
    with open(path, 'r') as f:
        return json.load(f)


private_data = load_json(config.private_json)


@bp.route('/legal-notice')
def legal_notice():
    return render_template(template_name_or_list='legal-notice.html', data=private_data)

@bp.route('/')
def festivals():
    festival_data = create_festival_data()
    return render_template(template_name_or_list='festivals.html', data=festival_data)


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(
        config.static_folder / 'favicons',
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@bp.route('/about')
def about_page():
    return render_template('about.html')
