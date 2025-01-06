from flask import Flask, render_template
import json

from forro_festivals.config import static_folder, private_json, root_path_flask

def load_private_data(path):
    """Saving Name+Location in a json not checked into the github repository."""
    with open(path, 'r') as f:
        return json.load(f)

def create_impressum_html(template='impressum.html'):
    private_data = load_private_data(private_json)

    app = Flask(__name__, root_path=root_path_flask)

    # The below 3 lines are needed since I added url_for into the base.html
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'https'

    with app.app_context():
        impressum = render_template(template, data=private_data)

    static_folder.mkdir(exist_ok=True)
    with open(f'{static_folder}/{template}', 'w') as file:
        file.write(impressum)


if __name__ == '__main__':
    create_impressum_html()
