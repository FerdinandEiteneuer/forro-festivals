"""
"""

from forro_festivals.config import db_path
from forro_festivals.db.db_api import update_db, init_db
from forro_festivals.scripts.query_forro_app import get_forro_app_events

def update_db_with_forro_app():
    if not db_path.exists():
        init_db(delete=False)

    fa_events = get_forro_app_events()
    update_db(fa_events)


if __name__ == '__main__':
    update_db_with_forro_app()
