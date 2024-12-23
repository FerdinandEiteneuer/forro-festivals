import json
import subprocess
import os

from flask import Flask, render_template, request

from forro_festivals.scripts.create_impressum import create_impressum
from forro_festivals.config import API_TOKEN, USERNAME, RELOAD_URL_PART, root_path_repository

def prepare():
    create_impressum()


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


@app.route('/')
def festivals():
    return render_template('festivals.html', festivals_data=festivals_data)

@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/impressum')
def impressum():
    return app.send_static_file('impressum.html')


@app.route(f'/reload-app', methods=['POST'])
def git_webhook():
    api_token = request.args.get('api_token')

    if api_token != API_TOKEN:
        return f"Unauthorized", 403

    if request.method == 'POST':
        try:
            os.chdir(root_path_repository)

            # Perform a git pull
            result = subprocess.run(['git', 'pull'], capture_output=True, text=True, check=True)
            print(f"Git pull successful: {result.stdout}")
        except Exception as e:
            return f"Error during git pull: {str(e)}", 500


        try:
            command = ['pip', 'install', '-e', '.']
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print("Output pip install:", result.stdout)
        except Exception as e:
            print("Error:", e.stderr)
            return f'Error during pip install: {str(e)}', 500

        # Next, we tell pythonanywhere to reload the app

        url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/webapps/www.forro-festivals.com/reload/"

        command = [
            "curl",
            "-X", "POST",
            "-H", f"Authorization: Token {API_TOKEN}",
            url
        ]
        command = ['bash', 'src/forro_festivals/scripts/reload-app.sh']
        command = ['touch', '/var/www/www_forro-festivals_com_wsgi.py']
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print("Output:", result.stdout, result.stderr)
        except Exception as e:
            print("Error during reloading:", e.stderr)
        #import requests
        #response = requests.post(
        #    'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain_name}/reload/'.format(
        #        username=USERNAME, domain_name='www.forro-festivals.com'
        #    ),
        #    headers={'Authorization': 'Token {token}'.format(token=api_token)}
        #)
        #if response.status_code == 200:
        #    print('reloaded OK')
        #else:
        #    print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))
        #    return "Error during reloading", 500

    return "We reached the end", 200


@app.route(f'/reload-bash', methods=['POST'])
def reload_bash():

    api_token = request.args.get('api_token')
    if api_token != API_TOKEN:
        return f"Unauthorized", 403

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
                print(err_str)
                return err_str, 500
        except Exception as e:
            return f"Exception during reloding: {str(e)}", 500

if __name__ == '__main__':
    prepare()
    app.run(debug=True)
