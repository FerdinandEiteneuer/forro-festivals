"""
Simple wrapper for a sqlite3 database

saves the Event datastructure together with
* id
* source
* created_at timestamp
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Optional
import logging

from forro_festivals.scripts.user import User
from forro_festivals.scripts.event import Event


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

    def create(self, delete=True):
        """
        Initializes db. Use with care, as it potentially removes existing db
        """

        if delete:
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

        with db_ops(self.path) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT UNIQUE NOT NULL,
                    permissions TEXT NOT NULL,
                    hashed_pw TEXT NOT NULL
                );
            """
            )

    def get_by_id(self, id, cls) -> Optional['cls']:
        with db_ops(self.path) as cursor:
            cursor.execute(f'SELECT * FROM {cls.sql_table()} WHERE id = ?', (id,))
            row = cursor.fetchone()
        if row:
            return cls.from_db_row(row)
        else:
            return None

    def delete_by_id(self, id, cls: type(User) | type(Event)) -> bool:
        with db_ops(self.path) as cursor:
            cursor.execute(f'DELETE FROM {cls.sql_table()} WHERE id = ?', (id, ))
            success = not cursor.rowcount == 0
            if not success:
                print(f"No row found with the given {id=}")
            return success

    def insert(self, obj: User | Event):
        cls = type(obj)
        try:
            cls(**obj.model_dump())
        except Exception:
            logging.error(f'Trying to insert inconsistent {obj=} into the database')
            raise

        insert_fields = ', '.join(obj.sql_insert_fields)
        question_marks = ', '.join(len(obj.sql_insert_fields) * ['?'])

        with db_ops(self.path) as cursor:
            sql_update = f'INSERT OR IGNORE INTO {obj.sql_table()} ({insert_fields}) VALUES ({question_marks})'
            cursor.execute(sql_update, obj.sql_values)

            # In case of duplicate, this returns 0. In case a valid entry is submitted, returns the id
            return cursor.lastrowid

    def get_all(self, cls: type(User) | type(Event)):
        with db_ops(self.path) as cursor:
            cursor.execute(f'SELECT * FROM {cls.sql_table()}')
            db_objects = cursor.fetchall()
        objects = []
        for db_object in db_objects:
            objects.append(cls.from_db_row(db_object))
        return objects

    def update_by_id(self, id, obj: User | Event):
        with db_ops(self.path) as cursor:
            fields = ', '.join(f'{field} = ?' for field in obj.sql_insert_fields)
            update = f'''
                UPDATE {obj.sql_table()}
                SET {fields}
                WHERE id = ?
            '''
            cursor.execute(update, obj.sql_values + (id, ))

    #### EVENT ####
    def delete_events_by_ids(self, event_ids: List[int] | int):
        if not isinstance(event_ids, list):
            event_ids = [event_ids]
        deletions = 0
        for event_id in event_ids:
            deletions += self.delete_by_id(event_id, cls=Event)
        return deletions

    def get_all_events(self) -> List[dict]:
        return self.get_all(Event)

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        return self.get_by_id(id=event_id, cls=Event)

    def get_size(self) -> int:
        return len(self.get_all_events())
