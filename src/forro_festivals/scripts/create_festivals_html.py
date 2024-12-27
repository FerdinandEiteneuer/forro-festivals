from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

from flask import Flask, render_template


from forro_festivals.config import static_folder, root_path_flask
from forro_festivals.scripts.event import Event
from forro_festivals.scripts.db import get_events_from_db


def create_festivals_html(events: List[Event], template='festivals.html'):
    festival_data = format_festival_data(events)

    app = Flask(__name__, root_path=root_path_flask)
    with app.app_context():
        festivals = render_template(template, data=festival_data)

    static_folder.mkdir(exist_ok=True)
    with open(f'{static_folder}/{template}', 'w') as file:
        file.write(festivals)


def format_festival_data(events: List[Event]):
    cutoff = datetime.today() - timedelta(days=30)

    events = [event for event in events if event.start > cutoff]
    events = sorted(events, key=lambda event: event.start)

    year_month_events = defaultdict(list)
    for event in events:
        year_month = event.start.strftime('%B %Y')  # January 2025
        festival = {
            'location': f'{event.city}, {event.country}',
            'date_start': event.start.strftime('%d.%m'),
            'date_end': event.end.strftime('%d.%m'),
            'link': event.link,
            'link_text': event.link_text,
        }
        year_month_events[year_month].append(festival)

    return dict(year_month_events)



if __name__ == '__main__':
    template = 'festivals.html'

    events = get_events_from_db()
    festival_data = format_festival_data(events)

    print(festival_data)

    app = Flask(__name__, root_path=root_path_flask)
    with app.app_context():
        festivals = render_template(template, data=festival_data)

    static_folder.mkdir(exist_ok=True)
    with open(f'{static_folder}/{template}', 'w') as file:
        file.write(festivals)
