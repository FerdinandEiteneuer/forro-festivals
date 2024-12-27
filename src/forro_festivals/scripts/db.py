"""
Simple wrapper for a sqlite3 database

saves the Event datastructure together with
* id
* source
* created_at timestamp
"""

import sqlite3
from contextlib import contextmanager
from typing import List
from datetime import datetime
import shutil

from forro_festivals.scripts.event import Event
from forro_festivals.config import db_path, db_backup_folder

def init_db():
    db = DataBase(db_path)
    db.create()

def backup_db():
    db_backup_folder.mkdir(exist_ok=True)
    timestamp = datetime.today().strftime('%y-%m-%d--%H-%m-%S')
    shutil.copy(db_path, db_backup_folder / f'festivals-{timestamp}')

def update_db(events: List[Event]):
    db = DataBase(db_path)
    N_before = db.get_size()

    for event in events:
        db.insert_event(event)

    N_after = db.get_size()

    if N_after - N_before != len(events):
        raise ValueError(f'Not all events could be inserted into the db')

def get_events_from_db():
    db = DataBase(db_path)
    return db.get_all_events()


@contextmanager
def db_ops(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        yield cur
    except Exception as e:
        conn.rollback()
        raise e
    else:
        conn.commit()
    finally:
        conn.close()

class DataBase:
    def __init__(self, path):
        self.path = path

    def create(self):
        """
        Initializes db. Use with care, as it potentially removes existing db
        """

        self.path.unlink(missing_ok=True)

        with db_ops(self.path) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_start TEXT NOT NULL,
                    date_end TEXT NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    organizer TEXT NOT NULL,
                    uuid TEXT NOT NULL,
                    link TEXT NOT NULL,
                    link_text TEXT NOT NULL,
                    validated  BOOLEAN DEFAULT TRUE,  -- indicates whether to show the event, defaults to TRUE
                    source TEXT NOT NULL,  -- who/what created this entry?
                    timestamp TEXT NOT NULL,  -- when was this entry created? 
                    UNIQUE (date_start, date_end, city, country, organizer)  -- prevents duplicates
                    -- Note: If i change the link_text manually in the db, readding the same event from the db 
                );
            """
            )
    def insert_event(self, event: Event):
        with db_ops(self.path) as cursor:
            cursor.execute("""
                INSERT OR IGNORE INTO events (date_start, date_end, city, country, organizer, uuid, link, link_text, validated, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, event.to_tuple()
            )

    def delete_event_by_id(self, event_id: int):
        with db_ops(self.path) as cursor:
            cursor.execute("""
                DELETE FROM events
                WHERE id = ?
            """, (event_id,))
            if cursor.rowcount == 0:
                print("No row found with the given id.")
            else:
                print(f"Deleted {cursor.rowcount} row(s).")

    def get_all_events(self) -> List[dict]:
        with db_ops(self.path) as cursor:
            cursor.execute("SELECT * FROM events")
            db_events = cursor.fetchall()

        events = []
        for db_event in db_events:
            event_ = dict(db_event)
            _ = event_.pop('id')
            events.append(Event(**event_))
        return events

    def get_size(self) -> int:
        return len(self.get_all_events())
