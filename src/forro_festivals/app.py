from flask import Flask, render_template
import json


app = Flask(__name__)


def load_private_data():
    with open('private.json', 'r') as f:
        return json.load(f)


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


if __name__ == '__main__':
    app.run(debug=True)
