import json

from forro_festivals.config import data_folder, private_json, db_backup_folder
from forro_festivals.db import db_api
from forro_festivals.db.db_api import init_db
from forro_festivals.misc.passwords import hash_password
from forro_festivals.models.user import User


def init_private_data():
    """The private data gets used in the legal-notice.html (Impressum)."""
    if not private_json.is_file():
        with open(private_json, 'w') as file:
            private_data = {
                'name': 'thats you',
                'adress': 'Your Adress 123',
                'city': 'Nice City',
                'email': 'thats-you@living-in-nice-city.com'
            }
            json.dump(private_data, file, indent=2)

def create_test_user():
    """Creates a first user."""
    user = User(
        email='admin',
        permissions='dashboard',
        hashed_pw=hash_password('admin')
    )
    db_api.insert_user(user)

def initialise():
    """Sets up folders and files required for running the app.

    * Datafolder
    * Logfolder
    * user database (just a json at the moment)
    * festival database (Should it exist, this will overwrite the database)
    * private data for impressum
    """
    data_folder.mkdir(exist_ok=True)
    db_backup_folder.mkdir(exist_ok=True)

    init_private_data()

    init_db(delete=True)
    create_test_user()

if __name__ == '__main__':
    initialise()
