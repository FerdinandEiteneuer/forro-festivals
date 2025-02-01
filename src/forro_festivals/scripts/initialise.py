import os
import json

from forro_festivals.config import data_folder, private_json, users_path, LOG_FOLDER, db_backup_folder
from forro_festivals.scripts.db_api import init_db

def init_private_data():
    """The private data gets used in the legal-notice.html (Impressum)"""
    if not private_json.is_file():
        with open(private_json, 'w') as file:
            private_data = {
                'name': 'thats you',
                'adress': 'Your Adress 123',
                'city': 'Nice City',
                'email': 'thats-you@living-in-nice-city.com'
            }
            json.dump(private_data, file, indent=2)

def init_users_data():
    """creates json with users that can access the /dashboard."""
    if not users_path.is_file():
        with open(users_path, 'w') as file:
            users = {
                'admin': {
                    'password': 'admin',
                    'permissions': ['dashboard'],
                }
            }
            json.dump(users, file, indent=2)

def initialise():
    """Sets up folders and files required for running the app.

    * Datafolder
    * Logfolder
    * user database (just a json at the moment)
    * festival database (Should it exist, this will overwrite the database)
    * private data for impressum
    """
    data_folder.mkdir(exist_ok=True)
    LOG_FOLDER.mkdir(exist_ok=True)
    db_backup_folder.mkdir(exist_ok=True)

    init_private_data()
    init_users_data()

    # TODO(fe) make a confirm step if you want to delete a db if exists?
    #          This would be consistent with init_private/users_data which dont overwrite
    init_db()


if __name__ == '__main__':
    initialise()
