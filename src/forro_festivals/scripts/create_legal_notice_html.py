from flask import render_template
import json

from forro_festivals.app import build_app
from forro_festivals.config import static_folder, private_json

def load_private_data(path):
    """Saving Name+Location in a json not checked into the github repository."""
    with open(path, 'r') as f:
        return json.load(f)

def create_legal_notice_html(template='legal-notice.html'):
    private_data = load_private_data(private_json)

    app = build_app()

    # The below 3 lines are needed since I added url_for into the base.html
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'

    with app.app_context():

        legal_notice = render_template(template, data=private_data)

    static_folder.mkdir(exist_ok=True)
    with open(f'{static_folder}/{template}', 'w') as file:
        file.write(legal_notice)


if __name__ == '__main__':
    create_legal_notice_html()
