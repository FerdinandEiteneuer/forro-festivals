"""
This module is responsible for creating the 'impressum' and the 'festivals' pages
"""

from forro_festivals.scripts.create_festivals_html import create_festivals_html
from forro_festivals.scripts.create_impressum_html import create_impressum_html
from forro_festivals.scripts.db import get_events_from_db

def render_html_pages():
    # impressum.html
    create_impressum_html()

    # festivals.html
    events = get_events_from_db()
    create_festivals_html(events)


if __name__ == '__main__':
    render_html_pages()
