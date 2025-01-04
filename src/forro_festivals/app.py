import subprocess
import os

from pydantic import ValidationError
from flask import Flask, render_template, request, send_from_directory, jsonify

from forro_festivals.scripts.create_impressum_html import create_impressum_html
from forro_festivals.config import API_TOKEN, root_path_repository, static_folder
from forro_festivals.scripts.event import Event


def prepare():
    create_impressum_html()


app = Flask(__name__)


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
    return send_from_directory(static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
    api_token = request.args.get('api_token')
    if api_token != API_TOKEN:
        print(f"Unauthorized {api_token[:4]}!={API_TOKEN[:4]}")
        return "Unauthorized", 403

    if request.method == 'POST':
        try:
            os.chdir(root_path_repository)

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
            success_msg = f'Event saved successfully! 🎉<br>Preview:<br>{event.to_html_string()}'
            return jsonify({'html_msg': success_msg}), 200
        except ValidationError as exc:
            err_msg = Event.human_readable_validation_error_explanation(exc)
            return jsonify({'error': err_msg}), 400

if __name__ == '__main__':
    prepare()
    app.run(debug=True)
