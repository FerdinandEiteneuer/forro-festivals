import sqlite3
from pathlib import Path
from contextlib import contextmanager

from forro_festivals.config import db_path


@contextmanager
def db_ops():
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        yield cur
    except Exception as e:
        # do something with exception
        conn.rollback()
        raise e
    else:
        conn.commit()
    finally:
        conn.close()


class DataBase:

    @staticmethod
    def create():
        """
        Initializes db. Use with care, as it potentially removes existing db
        """

        db_path.unlink(missing_ok=True)

        with db_ops() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_start TEXT NOT NULL,
                    date_end TEXT NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    link TEXT NOT NULL,
                    UNIQUE (date_start, date_end, city, country)  -- Prevent duplicates
                );
            """
            )

    @staticmethod
    def insert_event(date_start, date_end, city, country, link):
        with db_ops() as cursor:
            cursor.execute("""
                INSERT OR IGNORE INTO events (date_start, date_end, city, country, link)
                VALUES (?, ?, ?, ?, ?)
            """, (date_start, date_end, city, country, link))

    @staticmethod
    def get_all_events():
        with db_ops() as cursor:
            cursor.execute("SELECT * FROM events")
            events = cursor.fetchall()
        return events


if __name__ == '__main__':

    db = DataBase()

    db.create()

    db.insert_event("2024-01-01", "2024-01-05", "Berlin", "Germany", "https://example.com")
    db.insert_event("2024-02-04", "2024-02-08", "Hannover", "Germany", "https://example2.com")

    # Example usage
    for event in db.get_all_events():
        print(event)
