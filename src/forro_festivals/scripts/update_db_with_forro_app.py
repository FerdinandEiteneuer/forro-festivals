"""
"""

from forro_festivals.config import db_path
from forro_festivals import db_api
from forro_festivals.scripts.query_forro_app import get_forro_app_events

def update_db_with_forro_app():
    if not db_path.exists():
        db_api.init_db(delete=False)

    fa_events = get_forro_app_events()
    db_api.update_db(fa_events)


if __name__ == '__main__':
    update_db_with_forro_app()
