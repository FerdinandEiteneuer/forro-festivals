"""
This module is responsible for
1. making a backup of the database
2. querying external sources of forro events (forro-app.com)
3. writing them into the database
"""

from forro_festivals.scripts.update_db_with_forro_app import update_db_with_forro_app
from forro_festivals import db_api

def daily_build():
    db_api.backup_db()
    update_db_with_forro_app()

if __name__ == '__main__':
    daily_build()
