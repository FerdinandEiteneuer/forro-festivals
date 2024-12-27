"""
This module is responsible for creating the 'impressum' and the 'festivals' pages
"""

from forro_festivals.config import db_path
from forro_festivals.scripts.create_festivals_html import create_festivals_html
from forro_festivals.scripts.create_impressum_html import create_impressum_html
from forro_festivals.scripts.db import update_db, backup_db, get_events_from_db, init_db
from forro_festivals.scripts.query_forro_app import get_forro_app_events


if __name__ == '__main__':

    if db_path.exists():
        backup_db()
    else:
        init_db()

    create_impressum_html()
    fa_events = get_forro_app_events()
    update_db(fa_events)

    events = get_events_from_db()
    create_festivals_html(events)
