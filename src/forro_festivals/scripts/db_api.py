from typing import List
from datetime import datetime
import shutil

from forro_festivals.scripts.user import User
from forro_festivals.scripts.db import DataBase
from forro_festivals.scripts.event import Event
from forro_festivals.config import db_path, db_backup_folder



def init_db(delete):
    db = DataBase(db_path)
    db.create(delete=delete)

def backup_db():
    db_backup_folder.mkdir(exist_ok=True)
    timestamp = datetime.today().strftime('%y-%m-%d--%H-%M-%S')
    shutil.copy(db_path, db_backup_folder / f'festivals-{timestamp}.db')

def update_db(events: List[Event]):
    db = DataBase(db_path)
    event_ids = []
    for event in events:
        event_id = db.insert_event(event)
        event_ids.append(event_id)
    return event_ids

def add_event_to_db(event: Event):
    db = DataBase(db_path)
    return db.insert(event)

def get_events_from_db():
    db = DataBase(db_path)
    return db.get_all_events()

def get_event_from_db_by_id(event_id: int):
    db = DataBase(db_path)
    return db.get_event_by_id(event_id=event_id)

def update_event_by_id(event_id: int, event: Event):
    db = DataBase(db_path)
    db.update_event_by_id(event_id=event_id, event=event)

def delete_events_by_ids(event_ids: List[int] | int):
    """Deletes events conveniently by supplying a string like
    event_ids = '1,3-5,10,19-29'
    """
    db = DataBase(db_path)
    db.delete_events_by_ids(event_ids=event_ids)

def insert_user(user: User):
    db = DataBase(db_path)
    db.insert(user)

def update_user(user: User):
    db = DataBase(db_path)
    db.update_by_id(user.id, user)

def get_users():
    db = DataBase(db_path)
    return db.get_all(User)

def get_user(id):
    db = DataBase(db_path)
    return db.get_by_id(id, User)

def delete_user(id):
    db = DataBase(db_path)
    return db.delete_by_id(id, User)

def user_exists(id):
    return id in [user.id for user in get_users()]
